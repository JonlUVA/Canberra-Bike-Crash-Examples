from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from cycling_dashboard_app import app
import numpy as np

df_raw_data = pd.read_csv('data/crashes.csv')

var_dashboard = html.Div(
    [
        html.Div([
            dcc.Graph(id='crashes_by_sunset_time'),
            dcc.RadioItems(
                id='select_sunset_nearest_minute',
                options=[
                    {'label': 'All', 'value': 0},
                    {'label': '1 minute', 'value': 1},
                    {'label': '5 minute', 'value': 5},
                    {'label': '10 minute', 'value': 10},
                    {'label': '15 minute', 'value': 15}
                ],
                value=5
            )
        ]),
        html.Div([
            dcc.Graph(id='crashes_by_street_lights'),
            dcc.RadioItems(
                id='bool_show_severity',
                options=[
                    {'label': 'Crashes', 'value': 0},
                    {'label': 'Severity', 'value': 1}
                ],
                value=0
            )
        ])
    ],
    className='vis_wrapper_2x1'
)


@app.callback(
    Output(component_id='crashes_by_sunset_time', component_property='figure'),
    Input(component_id='select_sunset_nearest_minute', component_property='value')
)
def crashes_by_sunset(sunset_nearest_minute):

    test_visual_data = df_raw_data[['sunset', 'cyclists']]

    if sunset_nearest_minute == 0:
        pass
    else:
        test_visual_data['sunset'] = \
            pd.to_datetime(test_visual_data["sunset"]).round(str(sunset_nearest_minute) + 'T').dt.time

    test_visual_data = test_visual_data.groupby(['sunset', 'cyclists'],
                                                as_index=False).agg({'cyclists': sum})
    fig = px.line(
        test_visual_data,
        x='sunset',
        y='cyclists'
    )

    return fig


@app.callback(
    Output(component_id='crashes_by_street_lights', component_property='figure'),
    Input(component_id='bool_show_severity', component_property='value')
)
def crashes_by_street_lights(show_severity):

    test_visual_data = df_raw_data[['number_of_lights', 'cyclists', 'dark', 'severity']]

    test_visual_data = test_visual_data[test_visual_data['dark'] == 1]

    if show_severity == 0:
        test_visual_data = \
            test_visual_data.groupby(['number_of_lights'], as_index=False).agg({'cyclists': sum})
        fig = px.bar(
            test_visual_data,
            x='number_of_lights',
            y='cyclists'
        )
    else:
        test_visual_data = \
            test_visual_data.groupby(['number_of_lights', 'severity'], as_index=False).agg({'cyclists': sum})
        fig = px.bar(
            test_visual_data,
            x='number_of_lights',
            y='cyclists',
            color='severity'
        )

    return fig
