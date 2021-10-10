from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from flask import request

#   Importing the app
from cycling_dashboard_app import app, server

#   Importing all the visuals
from apps import cycling_visual_one
from apps import cycling_visual_two
from apps import cycling_visual_three
from apps import cycling_visual_four

######################################################################
#                          SETTING UP HTML                           #
######################################################################
app.layout = html.Div(
    id='main',
    children=[
        #   Pathname being used to select first visual
        dcc.Location(id='url', refresh=False, pathname='/apps/visual_one'),
        #   Side Navigation
        html.Div(
            id='side_menu',
            children=[
                html.H1(children='Select a Dashboard:'),
                dcc.Link('Location', href='/apps/visual_one'),
                dcc.Link('Weather', href='/apps/visual_two'),
                dcc.Link('Lighting', href='/apps/visual_three'),
                dcc.Link('Time and Day', href='/apps/visual_four'),
                dcc.Link('Close', href='/close')
            ]
        ),
        #   Visuals from files go here (Output Div)
        html.Div(
            id='output',
            children=[]
        )
    ]
)

######################################################################
#                          SETTING UP APP                            #
######################################################################
"""
    Based on the pathname the app will return the variable var_dashboard
    as children in the output div
"""
@app.callback(
    Output(component_id='output', component_property='children'),
    [Input(component_id='url', component_property='pathname')]
)
def display_dashboard(pathname):
    """
    :param pathname: The name of the visual the user is looking at
    :return: the visuals from py file
    """
    if pathname == '/apps/visual_one':
        return cycling_visual_one.var_dashboard
    elif pathname == '/apps/visual_two':
        return cycling_visual_two.var_dashboard
    elif pathname == '/apps/visual_three':
        return cycling_visual_three.var_dashboard
    elif pathname == '/apps/visual_four':
        return cycling_visual_four.var_dashboard
    elif pathname == '/close':
        func = request.environ.get('werkzeug.server.shutdown')
        func()
        return html.P('Sever Closed Successfully')
    else:
        return html.P('Error 404: Page not found...')


#if __name__ == '__main__':
#    app.run_server(debug=True, dev_tools_ui=False)
