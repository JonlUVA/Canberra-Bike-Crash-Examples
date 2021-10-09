import pandas as pd
import numpy as np

from dash import html
from dash import dcc
from dash.dependencies import Input, Output

import plotly.express as px

from cycling_dashboard_app import app
from apps.cycling_visual_global_functions import *

colors_list = get_colors()

######################################################################
#                       GETTING THE DATASETS                         #
######################################################################

"""
    DATASET 1: Crash Count
    Columns = cyclists, rainfall, severity
"""
df_crashes, df_cyclists = get_data_for_vis(1)

df_crash_count_data = df_crashes.copy()

df_crash_count_data = df_crash_count_data[
    ['cyclists', 'rainfall_amount_(millimetres)', 'severity']]

temp_df_rainfall = df_crash_count_data[df_crash_count_data['rainfall_amount_(millimetres)'] != 0]
temp_df_rainfall = temp_df_rainfall[temp_df_rainfall['rainfall_amount_(millimetres)'] != 0]
q75, q25 = np.percentile(temp_df_rainfall['rainfall_amount_(millimetres)'], [75, 25])
median = np.median(temp_df_rainfall['rainfall_amount_(millimetres)'])

rainfall_category_conditions = {
    'none':
        (df_crash_count_data['rainfall_amount_(millimetres)'] <= 0),
    'light':
        (df_crash_count_data['rainfall_amount_(millimetres)'] <= q25) &
        (df_crash_count_data['rainfall_amount_(millimetres)'] > 0),
    'moderate':
        (df_crash_count_data['rainfall_amount_(millimetres)'] > q25) &
        (df_crash_count_data['rainfall_amount_(millimetres)'] <= median),
    'heavy':
        (df_crash_count_data['rainfall_amount_(millimetres)'] > median) &
        (df_crash_count_data['rainfall_amount_(millimetres)'] <= q75),
    'violent':
        (df_crash_count_data['rainfall_amount_(millimetres)'] > q75)
}
# ADDING A NEW COLUMN TO THE DATAFRAME
df_crash_count_data['rainfall_category'] = np.select(
    rainfall_category_conditions.values(),
    rainfall_category_conditions.keys(),
    default='none'
)

"""
    DATASET 2: Crash Rate
    Columns = average_number_of_cyclists, rainfall, crash_count
"""
df_crash_rate_data = df_cyclists.copy()

df_crash_rate_data = df_crash_rate_data[
    ['macarthur_ave_display', 'rainfall_amount_(millimetres)', 'daily_crash_count']]

df_crash_rate_data['crash_rate'] = \
    (df_crash_rate_data['daily_crash_count']/df_crash_rate_data['macarthur_ave_display']) * 100

df_crash_rate_data['crash_rate'].replace(np.inf, 0, inplace=True)

temp_df_rainfall = df_crash_rate_data[df_crash_rate_data['rainfall_amount_(millimetres)'] != 0]
# FILTERING FOR THE RAINFALL DATA
temp_df_rainfall = temp_df_rainfall[temp_df_rainfall['rainfall_amount_(millimetres)'] != 0]
# DETERMINING THE INTER QUARTILE RANGE
q75, q25 = np.percentile(temp_df_rainfall['rainfall_amount_(millimetres)'], [75, 25])
# CALCULATING THE MEDIA
median = np.median(temp_df_rainfall['rainfall_amount_(millimetres)'])
rainfall_category_conditions = {
    'none':
        (df_crash_rate_data['rainfall_amount_(millimetres)'] <= 0),
    'light':
        (df_crash_rate_data['rainfall_amount_(millimetres)'] <= q25) &
        (df_crash_rate_data['rainfall_amount_(millimetres)'] > 0),
    'moderate':
        (df_crash_rate_data['rainfall_amount_(millimetres)'] > q25) &
        (df_crash_rate_data['rainfall_amount_(millimetres)'] <= median),
    'heavy':
        (df_crash_rate_data['rainfall_amount_(millimetres)'] > median) &
        (df_crash_rate_data['rainfall_amount_(millimetres)'] <= q75),
    'violent':
        (df_crash_rate_data['rainfall_amount_(millimetres)'] > q75)
}

df_crash_rate_data['rainfall_category'] = np.select(
    rainfall_category_conditions.values(),
    rainfall_category_conditions.keys(),
    default='none'
)


######################################################################
#                      CREATING THE HTML PAGE                        #
######################################################################
var_dashboard = html.Div(
    [
        html.Div(
            [
                html.H1(children='Cyclist Crashes and Crash Rate by Rainfall')
            ],
            className='span_horizontal_2'
        ),
        html.Div(
            [
                html.H3(children='Filter by Rainfall:'),
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
            ],
            className='span_horizontal_2 visual'
        ),
        html.Div(
            id='rainfall_crash_count_and_rate',
            children=[
                html.Div(
                    [
                        html.H3(children='Choose Calculation:'),
                        dcc.RadioItems(
                            id='selected_crash_calc',
                            options=[
                                {
                                    'value': 1,
                                    'label': 'Crash Rate %'
                                },
                                {
                                    'value': 0,
                                    'label': 'Crash Count'
                                }
                            ],
                            value=1,
                            labelStyle={'display': 'block'}
                        ),
                        html.H3(children='Choose Visualisation:', className='mt-10'),
                        dcc.RadioItems(
                            id='selected_chart_type',
                            options=[
                                {
                                    'value': 1,
                                    'label': 'Pie Chart'
                                },
                                {
                                    'value': 0,
                                    'label': 'Bar Chart'
                                }
                            ],
                            value=0,
                            labelStyle={'display': 'block'}
                        )
                    ],
                    className='pt-50'
                ),
                dcc.Graph(id='crashes_by_rainfall')
            ],
            className='visual'
        ),
        html.Div(
            [
                dcc.Graph(id='crash_severity_by_rainfall')
            ],
            className='visual'
        )
    ],
    className='wrapper_2x1'
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
        color='severity',
        color_discrete_sequence=colors_list,
        title='Crash Severity by Rainfall',
        labels={
            'cyclists': 'Cyclists',
            'crash_rate': 'Crash Rate (%)',
            'rainfall_category': 'Rainfall Type',
            'light': 'Light',
            'moderate': 'Moderate',
            'heavy': 'Heavy',
            'violent': 'Violent',
            'none': 'None',
            'severity': 'Severity'
        }
    )

    fig = update_fig_layout(fig)

    return fig


def cycling_crashes_by_rainfall(data_set, crash_calc, crash_calc_agg, chart_type):
    vis_df = data_set
    if crash_calc_agg == 'mean':
        vis_df = vis_df.groupby(['rainfall_category'], as_index=False).agg({crash_calc: np.mean})
    elif crash_calc == 'sum':
        vis_df = vis_df.groupby(['rainfall_category'], as_index=False).agg({crash_calc: sum})

    if chart_type == 1:
        fig = px.pie(
            vis_df,
            values=crash_calc,
            names='rainfall_category',
            color_discrete_sequence=colors_list,
            title='Crash Rate (%) by Rainfall',
            labels={
                'cyclists': 'Cyclists',
                'crash_rate': 'Crash Rate (%)',
                'rainfall_category': 'Rainfall Type',
                'light': 'Light',
                'moderate': 'Moderate',
                'heavy': 'Heavy',
                'violent': 'Violent',
                'none': 'None'
            }
        )
    else:
        fig = px.bar(
            vis_df,
            y=crash_calc,
            x='rainfall_category',
            color_discrete_sequence=colors_list,
            title='Crash Rate (%) by Rainfall',
            labels={
                'cyclists': 'Cyclists',
                'crash_rate': 'Crash Rate (%)',
                'rainfall_category': 'Rainfall Type',
                'light': 'Light',
                'moderate': 'Moderate',
                'heavy': 'Heavy',
                'violent': 'Violent',
                'none': 'None'
            }
        )

    fig = update_fig_layout(fig)

    return fig


@app.callback(
    [
        Output(component_id='crashes_by_rainfall', component_property='figure'),
        Output(component_id='crash_severity_by_rainfall', component_property='figure'),
        Output(component_id='selected_chart_type', component_property='style'),
        Output(component_id='selected_chart_type', component_property='value')
    ],
    [
        Input(component_id='selected_crash_calc', component_property='value'),
        Input(component_id='selected_chart_type', component_property='value'),
        Input(component_id='rainfall_filter_list', component_property='value')
    ]
)
def rainfall_crash_count_visuals(crash_calc, chart_type, rainfall_categories):

    crash_count_data_set = df_crash_count_data.copy()
    crash_count_data_set = crash_count_data_set[crash_count_data_set['rainfall_category'].isin(rainfall_categories)]
    if crash_calc == 0:
        crash_calc = 'cyclists'
        crash_calc_agg = 'sum'
        crash_calc_data_set = crash_count_data_set
        select_chart_style = {'display': 'none'}
        select_chart_value = 1
    else:
        crash_calc = 'crash_rate'
        crash_calc_agg = 'mean'
        crash_calc_data_set = df_crash_rate_data.copy()
        crash_calc_data_set = crash_calc_data_set[crash_calc_data_set['rainfall_category'].isin(rainfall_categories)]
        select_chart_style = {'display': 'block'}
        select_chart_value = chart_type

    fig_rainfall_crashes = cycling_crashes_by_rainfall(
        crash_calc_data_set, crash_calc, crash_calc_agg, select_chart_value)

    fig_rainfall_crash_severity = cycling_crash_severity_by_rainfall(crash_count_data_set)

    return fig_rainfall_crashes, fig_rainfall_crash_severity, select_chart_style, select_chart_value
