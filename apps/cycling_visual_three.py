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
            html.Div([
                html.H3(children='Group by Nearest Minute:'),
                dcc.RadioItems(
                    id='select_sunset_nearest_minute',
                    options=[
                        {'label': '1 Minute', 'value': 1},
                        {'label': '5 Minute', 'value': 5},
                        {'label': '10 Minute', 'value': 10},
                        {'label': '15 Minute', 'value': 15}
                    ],
                    value=5,
                    labelStyle={'display': 'block'}
                )
            ]),
            dcc.Graph(id='crashes_by_sunset_time')
        ], className='visual visual_3_wrapper'),
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


def crashes_by_sunset(data_set, sunset_nearest_minute):
    if sunset_nearest_minute == 0:
        pass
    else:
        data_set['sunset'] = pd.to_datetime(data_set["sunset"]).round(str(sunset_nearest_minute) + 'T').dt.time

    vis_df = data_set.groupby(['sunset', 'cyclists'], as_index=False).agg({'cyclists': sum})

    fig = px.line(
        vis_df,
        x='sunset',
        y='cyclists',
        title='Sunset Time and Night Time Crashes',
        labels={
            'cyclists': 'Cyclists',
            'severity': 'Severity',
            'number_of_lights': 'Number of Lights',
            'sunset': 'Sunset'
        }
    )

    fig = update_fig_layout(fig)

    return fig


def crashes_by_street_lights(data_set, show_severity):
    if show_severity == 0:
        vis_df = data_set.groupby(['number_of_lights'], as_index=False).agg({'cyclists': sum})
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
        vis_df = data_set.groupby(['number_of_lights', 'severity'], as_index=False).agg({'cyclists': sum})
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
        Input(component_id='select_sunset_nearest_minute', component_property='value'),
        Input(component_id='bool_show_severity', component_property='value')
    ]
)
def crashes_by_lighting_visuals(sunset_nearest_minute, show_severity):
    vis_df = df_crash_data[['number_of_lights', 'sunset', 'cyclists', 'dark', 'severity']]
    vis_df = vis_df[vis_df['dark'] == 1]

    fig_crashes_by_sunset = crashes_by_sunset(vis_df, sunset_nearest_minute)
    fig_crashes_by_street_lighting = crashes_by_street_lights(vis_df, show_severity)

    return fig_crashes_by_sunset, fig_crashes_by_street_lighting
