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

app.layout = html.Div(
    id='main',
    children=[
        dcc.Location(id='url', refresh=False),
        html.Div(
            id='side_menu',
            children=[
                dcc.Link('visual one', href='/apps/visual_one'),
                dcc.Link('visual two', href='/apps/visual_two'),
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
        return visual_one.var_layout
    else:
        return html.P('Error 404: Page not found...')
        # return visual_two.layout


if __name__ == '__main__':
    app.run_server(debug=True)
