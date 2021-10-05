from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from cycling_dashboard_app import app
import numpy as np


"""
@app.callback(
    Output(component_id='boxplot_rain_distribution', component_property='figure'),
    Input(component_id='boxplot_rain_distribution', component_property='figure')
)
"""

df_raw_data = pd.read_csv('data/crashes.csv')
df_crashes_by_rainfall = df_raw_data[['cyclists', 'rainfall_amount_(millimetres)', 'severity']]

#https://www.statology.org/interquartile-range-python/#:~:text=It%20is%20calculated%20as%20the%20difference%20between%20the,of%20how%20to%20use%20this%20function%20in%20practice.
df_rainfall = df_crashes_by_rainfall[df_crashes_by_rainfall['rainfall_amount_(millimetres)'] != 0]
q75, q25 = np.percentile(df_rainfall['rainfall_amount_(millimetres)'], [75, 25])
median = np.median(df_rainfall['rainfall_amount_(millimetres)'])


rainfall_category_conditions = [
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] <= 0),
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] <= q25) &
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] > 0),
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] > q25) &
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] <= median),
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] > median) &
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] <= q75),
    (df_crashes_by_rainfall['rainfall_amount_(millimetres)'] > q75)
]

rainfall_category_values = [
    'none',
    'light',
    'moderate',
    'heavy',
    'violent'
]

df_crashes_by_rainfall['rainfall_category'] = np.select(
    rainfall_category_conditions,
    rainfall_category_values
)

#print(df_crashes_by_rainfall[df_crashes_by_rainfall['rainfall_category'] != 'none'])

def rainfall_distribution_over_period():
    fig = px.box(
        df_raw_data[df_raw_data['rainfall_amount_(millimetres)'] != 0],
        y='rainfall_amount_(millimetres)',
        points=False,
        log_y=True
    )
    print()
    return fig


var_dashboard = html.Div([
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
           labelStyle={'display': 'block'}
       )
    ]),
    html.Div([
        dcc.Graph(id='crashes_by_rainfall')
    ]),
    html.Div([
        dcc.Graph(figure=rainfall_distribution_over_period(), id='boxplot_rain_distribution')
    ])
])


@app.callback(
    Output(component_id='crashes_by_rainfall', component_property='figure'),
    Input(component_id='rainfall_filter_list', component_property='value')
)
def cycling_crashed_by_rainfall(rainfall_categories):

    fig_df = df_crashes_by_rainfall
    fig_df = fig_df[fig_df['rainfall_category'].isin(rainfall_categories)]
    fig_df = fig_df.groupby(['rainfall_category', 'severity'], as_index=False).agg({'cyclists': sum})
    fig = px.bar(fig_df, x='rainfall_category', y='cyclists', color='severity')

    return fig
