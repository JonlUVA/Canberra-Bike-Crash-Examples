import pandas as pd
import numpy as np

import plotly.express as px

from dash import html
from dash import dcc
from dash.dependencies import Input, Output

from cycling_dashboard_app import app
from apps.cycling_visual_global_functions import *

df_crashes = get_data_for_vis(0)
df_crash_data = df_crashes.copy()

var_dashboard = html.Div(
    [
        html.Div(
            [
                html.H1(children='Cyclist Crashes During Low Light')
            ],
            className='span_horizontal_2'
        ),
        html.Div([
            dcc.Graph(id='crashes_by_sunset_time')
        ], className='visual'),
        html.Div([
            html.Div([
                html.H3(children='Show Severity:'),
                dcc.RadioItems(
                    id='bool_show_severity',
                    options=[
                        {'label': 'Crashes', 'value': 0},
                        {'label': 'Severity', 'value': 1}
                    ],
                    value=0,
                    labelStyle={'display': 'block'}
                )

            ]),
            dcc.Graph(id='crashes_by_street_lights'),

        ], className='visual visual_3_wrapper')
    ],
    className='wrapper_2x1'
)


def crashes_by_month(data_set):
    vis_df = data_set.copy()
    vis_df = vis_df[vis_df['dark'] == 1]
    vis_df['month'] = pd.to_datetime(vis_df['date']).dt.month_name()
    #vis_df['sunset_min'] = vis_df['sunset'] - pd.Timedelta(hours=1)
    #vis_df['sunset_max'] = vis_df['sunset'] + pd.Timedelta(hours=1)
    #vis_df = vis_df[(vis_df['time'] >= vis_df['sunset_min']) & (vis_df['time'] <= vis_df['sunset_max'])]

    vis_df = vis_df.groupby(['month'], as_index=False).agg({'cyclists': sum})

    fig = px.bar(
        vis_df,
        x='month',
        y='cyclists',
        title='Night Crashes by Month',
        labels={
            'cyclists': 'Cyclists',
            'severity': 'Severity',
            'number_of_lights': 'Number of Lights',
            'month': 'Month'
        }
    )

    fig = update_fig_layout(fig)

    fig.update_xaxes(categoryorder='array', categoryarray=['January', 'February', 'March', 'April', 'May', 'June',
                                                           'July', 'August', 'September', 'October', 'November', 'December'])

    return fig


def crashes_by_street_lights(data_set, show_severity):
    vis_df = data_set.copy()
    vis_df = vis_df[vis_df['dark'] == 1]

    if show_severity == 0:
        vis_df = vis_df.groupby(['number_of_lights'], as_index=False).agg({'cyclists': sum})
        fig = px.bar(
            vis_df,
            x='number_of_lights',
            y='cyclists',
            title='Crashes by Street Light Count',
            labels={
                'cyclists': 'Cyclists',
                'severity': 'Severity',
                'number_of_lights': 'Number of Lights',
                'sunset': 'Sunset'
            }
        )
    else:
        vis_df = vis_df.groupby(['number_of_lights', 'severity'], as_index=False).agg({'cyclists': sum})
        fig = px.bar(
            vis_df,
            x='number_of_lights',
            y='cyclists',
            color='severity',
            title='Crash Severity by Street Light Count',
            labels={
                'cyclists': 'Cyclists',
                'severity': 'Severity',
                'number_of_lights': 'Number of Lights',
                'sunset': 'Sunset'
            }
        )

    fig = update_fig_layout(fig)

    return fig


@app.callback(
    [
        Output(component_id='crashes_by_sunset_time', component_property='figure'),
        Output(component_id='crashes_by_street_lights', component_property='figure')
    ],
    [
        Input(component_id='bool_show_severity', component_property='value')
    ]
)
def crashes_by_lighting_visuals(show_severity):
    vis_df = df_crash_data[['number_of_lights', 'sunset', 'date', 'time', 'cyclists', 'dark', 'severity']]

    fig_crashes_by_month = crashes_by_month(vis_df)
    fig_crashes_by_street_lighting = crashes_by_street_lights(vis_df, show_severity)

    return fig_crashes_by_month, fig_crashes_by_street_lighting
