import plotly.express as px

from dash import html
from dash import dcc
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np

from cycling_dashboard_app import app
from apps.cycling_visual_global_functions import *

#   Getting Custom Colors
colors_list = get_colors()

#   Getting Required Data
df_crashes = get_data_for_vis(0)

######################################################################
#                          SETTING UP HTML                           #
######################################################################

var_dashboard = html.Div(
    [
        html.Div(
            [
                html.H1(children='Cyclist Crashes by Location and Time of Day'),
                dcc.Checklist(
                    id='selected_day_of_week',
                    options=[
                        {'label': 'Sunday', 'value': 'Sunday'},
                        {'label': 'Monday', 'value': 'Monday'},
                        {'label': 'Tuesday', 'value': 'Tuesday'},
                        {'label': 'Wednesday', 'value': 'Wednesday'},
                        {'label': 'Thursday', 'value': 'Thursday'},
                        {'label': 'Friday', 'value': 'Friday'},
                        {'label': 'Saturday', 'value': 'Saturday'}
                    ],
                    value=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                )
            ]
        ),

        #   VISUAL ONE AND TWO
        html.Div([
            html.Div([
                dcc.Graph(id='crashes_by_time_of_day_and_location', style={'height': '30vh', 'width': '40vw'}),
                html.H3(children='Filter by Time of Day:'),
                dcc.RangeSlider(
                    id='selected_time_of_day',
                    min=0,
                    max=23,
                    value=[0, 23],
                    marks={
                        0: '12:00am',
                        8: '9:00am',
                        11: '12:00pm',
                        16: '5:00pm',
                        23: '11:59pm'
                    }
                )
            ], className='visual'),
            html.Div([
                dcc.Graph(id='crashes_by_time_of_day', style={'height': '100%', 'width': '100%'})
            ], className='visual'),
        ], className='wrapper_2x1'),

        #   VISUAL 3
        html.Div([
            html.Div([
                html.H3(children='Group In:'),
                dcc.RadioItems(
                    id='select_crash_time_nearest_minute',
                    options=[
                        {'label': '15 Minutes', 'value': 15},
                        {'label': '30 Minutes', 'value': 30},
                        {'label': '1 Hours', 'value': 60},
                        {'label': '2 Hours', 'value': 120},
                        {'label': '4 Hours', 'value': 240}
                    ],
                    value=60,
                    labelStyle={'display': 'block'}
                )
            ]),
            dcc.Graph(id='crashes_by_day_of_week')
        ], className='visual visual_3_wrapper'),
    ],
    className='wrapper_1x3'
)


#########################################
#          GENERATING VISUALS           #
#########################################


def crashes_by_time_of_day_and_location(data_set, time_filter_vals):
    """
    :param time_filter_vals: gets user selected times 0 - 23
    :return: map scatter plot with crashes between user selected times
    """
    vis_df = data_set.copy()
    vis_df = vis_df.set_axis(pd.to_datetime(vis_df['time']), axis='index')
    #   Making the user input time strings
    start_time = str(time_filter_vals[0]).zfill(2) + ':00'
    finish_time = str(time_filter_vals[1]).zfill(2) + ':59'
    #   Getting rows where time is between user selected inputs
    vis_df = vis_df.between_time(start_time, finish_time)
    vis_df = vis_df.groupby(['suburb', 'lat', 'long'], as_index=False).agg({'cyclists': sum})

    fig = px.scatter_mapbox(
        vis_df,
        lon='long',
        lat='lat',
        title='Crashes between ' + start_time + ' and ' + finish_time,
        mapbox_style='carto-darkmatter',
        zoom=9.25,
        color_discrete_sequence=colors_list,
        center={'lat': -35.3222, 'lon': 149.1287}
    )

    fig = update_fig_layout(fig)

    return fig


def crashes_by_day_of_week(data_set):
    """
    :return: A bar graph containing the crash count by day
    """
    vis_df = data_set.copy()

    vis_df = vis_df.groupby(['day_of_week'], as_index=False).agg({'cyclists': sum})

    fig = px.bar(
        vis_df,
        x='day_of_week',
        y='cyclists',
        title='Crashes by Day of the Week',
        color_discrete_sequence=colors_list,
        labels={
            'cyclists': 'Cyclists',
            'time': 'Time',
            'day_of_week': 'Day'
        }
    )

    fig = update_fig_layout(fig)

    fig.update_xaxes(categoryorder='array', categoryarray=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                                           'Friday', 'Saturday'])

    return fig


def crashes_by_time_of_day(data_set, tod_nearest_minute):
    """
    :param tod_nearest_minute: The user selected time grouping
    :return: A bar graph showing the crashes by user selected time grouping
    """
    vis_df = data_set.copy()

    #   Rounding time based on user input
    vis_df['time'] = pd.to_datetime(vis_df['time']).round(str(tod_nearest_minute) + 'T').dt.time

    vis_df = vis_df.groupby(['time'], as_index=False).agg({'cyclists': sum})

    fig = px.bar(
        vis_df,
        x='time',
        y='cyclists',
        title='Crashes by Time',
        color_discrete_sequence=colors_list,
        labels={
            'cyclists': 'Cyclists',
            'time': 'Time',
            'day_of_week': 'Day'
        }
    )

    fig = update_fig_layout(fig)

    return fig


@app.callback(
    [
        Output(component_id='crashes_by_time_of_day_and_location', component_property='figure'),
        Output(component_id='crashes_by_day_of_week', component_property='figure'),
        Output(component_id='crashes_by_time_of_day', component_property='figure'),
    ],
    [
        Input(component_id='select_crash_time_nearest_minute', component_property='value'),
        Input(component_id='selected_day_of_week', component_property='value'),
        Input(component_id='selected_time_of_day', component_property='value')
    ]
)
def crashes_by_time_visual(tod_nearest_minute, selected_dow, selected_tod):
    """
    :param tod_nearest_minute: the selected time grouping
    :param selected_dow: the selected day of the week
    :param selected_tod: the selected time of day
    :return: crashes by location vis, crashes by day vis, crashes by time vis
    """
    vis_df = df_crashes[['district', 'suburb', 'date', 'time', 'cyclists', 'lat', 'long']].copy()

    vis_df['day_of_week'] = pd.to_datetime(vis_df['date']).dt.day_name()

    vis_df = vis_df[vis_df['day_of_week'].isin(selected_dow)]

    fig_crashes_by_hour = crashes_by_time_of_day(vis_df, tod_nearest_minute)

    fig_crashes_by_day_of_week = crashes_by_day_of_week(vis_df)

    fig_crashes_by_time_and_location = crashes_by_time_of_day_and_location(vis_df, selected_tod)

    return fig_crashes_by_time_and_location, fig_crashes_by_hour, fig_crashes_by_day_of_week


