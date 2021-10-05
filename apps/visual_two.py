from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from cycling_dashboard_app import app

var_dashboard = html.Div([
   html.Div([
       dcc.Graph(id='boxplot_rain_distribution')
   ])
])

df_raw_data = pd.read_csv('data/crashes.csv')


@app.callback(
    Output(component_id='boxplot_rain_distribution', component_property='figure'),
    Input(component_id='boxplot_rain_distribution', component_property='figure')
)
def rainfall_distribution_over_period(placeholder):
    fig = px.box(
        df_raw_data[df_raw_data['rainfall_amount_(millimetres)'] != 0],
        y='rainfall_amount_(millimetres)',
        #points='all',
        points=False,
        log_y=True
    )
    print(placeholder)
    return fig