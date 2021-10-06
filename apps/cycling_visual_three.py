from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from cycling_dashboard_app import app
import numpy as np

var_dashboard = html.Div(
    [
        html.Div([
            dcc.Graph(figure=rainfall_distribution_over_period(), id='boxplot_rain_distribution')
        ])
    ],
    className='vis_wrapper_2x1'
)