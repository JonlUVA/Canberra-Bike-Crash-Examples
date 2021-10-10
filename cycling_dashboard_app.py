"""
@author:  Hugh Porter
@uid:     u7398670

This file is just setting up the app
"""

import dash

app = dash.Dash(__name__, suppress_callback_exceptions=True)

server = app.server
