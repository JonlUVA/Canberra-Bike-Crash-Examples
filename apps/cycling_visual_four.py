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
            dcc.Graph(id='crashes_by_time_of_day'),
        ]),
        dcc.RadioItems(
            id='select_crash_time_nearest_minute',
            options=[
                {'label': 'All', 'value': 0},
                {'label': '1 minute', 'value': 1},
                {'label': '5 minute', 'value': 5},
                {'label': '10 minute', 'value': 10},
                {'label': '15 minute', 'value': 15}
            ],
            value=5
        )
    ],
    className='vis_wrapper_2x1'
)


@app.callback(
    Output(component_id='crashes_by_time_of_day', component_property='figure'),
    Input(component_id='select_crash_time_nearest_minute', component_property='value')
)
def crashes_by_time_of_day(tod_nearest_minute):

    vis_df = df_raw_data[['time', 'cyclists']]

    if tod_nearest_minute == 0:
        pass
    else:
        vis_df['time'] = \
            pd.to_datetime(vis_df["time"]).round(str(tod_nearest_minute) + 'T').dt.time

    fig = px.scatter(
        vis_df,
        x='time',
        y='cyclists'
    )

    return fig


