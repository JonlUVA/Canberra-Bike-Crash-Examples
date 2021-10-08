from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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

    vis_df = vis_df.groupby(['time', 'cyclists'], as_index=False).agg({'cyclists': sum})

    #fig = px.Figure()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=vis_df['time'],
        y=vis_df['cyclists']
    ))

    #reg = pd.ols(y=vis_df['cyclists'], x=vis_df['time'])
    # generate a regression line with px

    vis_df['time_str'] = pd.to_datetime(['time'], format='%H:%M:%S %p')

    help_fig = px.scatter(vis_df, x=vis_df['time_str'], y=vis_df['cyclists'], trendline="ols")
    # extract points as plain x and y
    x_trend = help_fig["data"][1]['x']
    y_trend = help_fig["data"][1]['y']

    #fig.add_trace(go.Scatter(x=x_trend, y=y_trend))

    return fig


