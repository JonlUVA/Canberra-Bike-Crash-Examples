from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from cycling_dashboard_app import app
import numpy as np




df_raw_data = pd.read_csv('data/crashes.csv')

test_visual_data = df_raw_data[['sunset', 'cyclists']]


test_visual_data['sunset_nearest_minute'] = pd.to_datetime(test_visual_data["sunset"]).round('1T').dt.time


def crashes_by_sunset(data_set):
    fig = px.line(
        test_visual_data,
        x='sunset_nearest_minute',
        y='cyclists'
    )
    return fig


var_dashboard = html.Div(
    [
        html.Div([
            dcc.Graph(figure=crashes_by_sunset(test_visual_data), id='crashes_by_lighting_conditions')
        ])
    ],
    className='vis_wrapper_2x1'
)









