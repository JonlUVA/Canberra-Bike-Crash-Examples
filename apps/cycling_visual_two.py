from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from cycling_dashboard_app import app
import numpy as np

######################################################################
#                        GETTING THE DATASET                         #
######################################################################

# DATA IN
df_raw_data = pd.read_csv('data/crashes.csv')
# SELECTING REQUIRED COLUMNS
df_crashes_by_rainfall = df_raw_data[['cyclists', 'rainfall_amount_(millimetres)', 'severity']]
#https://www.statology.org/interquartile-range-python/#:~:text=It%20is%20calculated%20as%20the%20difference%20between%20the,of%20how%20to%20use%20this%20function%20in%20practice.

# GETTING THE RAIN FALL CATEGORIES
# FILTERING FOR THE RAINFALL DATA
df_rainfall = df_crashes_by_rainfall[df_crashes_by_rainfall['rainfall_amount_(millimetres)'] != 0]
# DETERMINING THE INTER QUARTILE RANGE
q75, q25 = np.percentile(df_rainfall['rainfall_amount_(millimetres)'], [75, 25])
# CALCULATING THE MEDIA
median = np.median(df_rainfall['rainfall_amount_(millimetres)'])
# DEFINING THE GROUPING
# https://towardsdatascience.com/efficient-implementation-of-conditional-logic-on-pandas-dataframes-4afa61eb7fce
rainfall_category_conditions = {
    'none': (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] <= 0),
    'light': (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] <= q25) &
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] > 0),
    'moderate': (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] > q25) &
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] <= median),
    'heavy': (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] > median) &
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] <= q75),
    'violent': (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] > q75)
}

copy_of_df_crashes_by_rainfall_category = df_crashes_by_rainfall.copy()
# ADDING A NEW COLUMN TO THE DATAFRAME
copy_of_df_crashes_by_rainfall_category.loc[:, 'rainfall_category'] = np.select(
    rainfall_category_conditions.values(),
    rainfall_category_conditions.keys(),
    default='none'
)


######################################################################
#                      CREATING THE HTML PAGE                        #
######################################################################
var_dashboard = html.Div(
    [
        html.Div([
           dcc.Checklist(
               id='rainfall_filter_list',
               options=[
                    {'label': 'None', 'value': 'none'},
                    {'label': 'Light', 'value': 'light'},
                    {'label': 'Moderate', 'value': 'moderate'},
                    {'label': 'Heavy', 'value': 'heavy'},
                    {'label': 'Violent', 'value': 'violent'}
               ],
               value=['none', 'light', 'moderate', 'heavy', 'violent'],
               labelStyle={'display': 'inline-block'}
           )
        ], className='col-2'),
        html.Div([
            dcc.Graph(id='crash_severity_by_rainfall')
        ]),
        html.Div([
           dcc.Graph(id='crashes_by_rainfall')
        ])
    ],
    className='vis_wrapper_2x1'
)

#########################################
#          GENERATING VISUALS           #
#########################################
"""
    INPUT(S):
    1. The user selected rainfall category/categories
    
    OUTPUT(S):
    1. The crash severity by rainfall category visual
"""


def cycling_crash_severity_by_rainfall(data_set):
    vis_df = data_set
    vis_df = vis_df.groupby(['rainfall_category', 'severity'], as_index=False).agg({'cyclists': sum})
    fig = px.bar(
        vis_df,
        x='rainfall_category',
        y='cyclists',
        color='severity'
    )
    return fig


def cycling_crashes_by_rainfall(data_set):
    vis_df = data_set
    vis_df = vis_df.groupby(['rainfall_category'], as_index=False).agg({'cyclists': sum})
    fig = px.pie(
        vis_df,
        values='cyclists',
        names='rainfall_category'
    )
    return fig


@app.callback(
    [
        Output(component_id='crashes_by_rainfall', component_property='figure'),
        Output(component_id='crash_severity_by_rainfall', component_property='figure')
    ],
    Input(component_id='rainfall_filter_list', component_property='value')
)
def rainfall_crash_count_visuals(rainfall_categories):
    data_set = copy_of_df_crashes_by_rainfall_category
    # Filtering DataFrame to only include rows in the rainfall categories (user input)
    data_set = data_set[data_set['rainfall_category'].isin(rainfall_categories)]

    fig_rainfall_crashes = cycling_crashes_by_rainfall(data_set)

    fig_rainfall_crash_severity = cycling_crash_severity_by_rainfall(data_set)

    return fig_rainfall_crashes, fig_rainfall_crash_severity
