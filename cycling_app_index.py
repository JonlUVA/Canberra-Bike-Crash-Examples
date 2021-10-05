import json
import plotly as plt
import plotly.express as px
import pandas as pd
import csv
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output


from cycling_dashboard_app import app
from cycling_dashboard_app import server
from apps import visual_one
from apps import visual_two

list_colors = [
    '#003f5c'
    '#2f4b7c'
    '#665191'
    '#a05195'
    '#d45087'
    '#f95d6a'
    '#ff7c43'
    '#ffa600'
]

app.layout = html.Div(
    id='main',
    children=[
        #pathname being used to select first visual
        dcc.Location(id='url', refresh=False, pathname='/apps/visual_one'),
        html.Div(
            id='side_menu',
            children=[
                dcc.Link('Cyclist Crashes by Suburb and District', href='/apps/visual_one'),
                dcc.Link('Cyclist Crashed and Weather', href='/apps/visual_two'),
                dcc.Link('visual three', href='/apps/visual_three'),
                dcc.Link('visual four', href='/apps/visual_four')
            ]
        ),
        html.Div(
            id='output',
            children=[]
        )
    ]
)


@app.callback(
    Output(component_id='output', component_property='children'),
    [Input(component_id='url', component_property='pathname')]
)
def display_dashboard(pathname):
    if pathname == '/apps/visual_one':
        return visual_one.var_dashboard
    elif pathname == '/apps/visual_two':
        return visual_two.var_dashboard
    else:
        return html.P('Error 404: Page not found...')
        # return visual_two.layout


if __name__ == '__main__':
    app.run_server(debug=True)
