"""
@author:  Hugh Porter
@uid:     u7398670
"""
import pandas as pd
import numpy as np

import plotly.express as px

from dash import html
from dash import dcc
from dash.dependencies import Input, Output

from cycling_dashboard_app import app
from apps.cycling_visual_global_functions import *

# Getting Colours for use in visual
colors_list = get_colors()
#   Getting Dataset required for vis.
df_crashes = get_data_for_vis(0)
#   Creating a copy of the dataset
df_crash_data = df_crashes.copy()

######################################################################
#                          SETTING UP HTML                           #
######################################################################

var_dashboard = html.Div(
    [
        html.Div(
            [
                html.H1(children='Cyclist Crashes During Low Light')
            ],
            className='span_horizontal_2'
        ),
        html.Div([
            #   Visual One - Crashed by Month
            dcc.Graph(id='crashes_by_sunset_time', style={'height': '50vh'})
        ], className='visual'),
        html.Div([
            html.Div([
                html.Div([
                    html.H3(children='Show Severity:'),
                    dcc.RadioItems(
                        id='bool_show_severity',
                        options=[
                            {'label': 'Crashes', 'value': 0},
                            {'label': 'Severity', 'value': 1}
                        ],
                        value=0,
                        labelStyle={'display': 'block'}
                    )
                ])
            ], className='center_items'),
            #   Visual Two - Crashed by Streetlight Count
            dcc.Graph(id='crashes_by_street_lights', style={'height': '50vh'}),

        ], className='visual visual_3_wrapper')
    ],
    className='wrapper_2x1'
)

######################################################################
#                        SETTING UP VISUALS                          #
######################################################################


def crashes_by_month(data_set):
    """"
        Filtering Dataset to only include crashes from night time
        Grouping crashes by month
        Visualising data as a bar graph
    """
    #   Making a copy of the data set
    vis_df = data_set.copy()
    vis_df = vis_df[vis_df['dark'] == 1]
    vis_df['month'] = pd.to_datetime(vis_df['date']).dt.month_name()

    vis_df = vis_df.groupby(['month'], as_index=False).agg({'cyclists': sum})

    fig = px.bar(
        vis_df,
        x='month',
        y='cyclists',
        color_discrete_sequence=colors_list,
        title='Night Crashes by Month',
        labels={
            'cyclists': 'Cyclists',
            'severity': 'Severity',
            'number_of_lights': 'Number of Lights',
            'month': 'Month'
        }
    )

    fig = update_fig_layout(fig)

    # Reordering X axis
    fig.update_xaxes(categoryorder='array', categoryarray=['January', 'February', 'March', 'April', 'May', 'June',
                                                           'July', 'August', 'September', 'October', 'November', 'December'])

    return fig


def crashes_by_street_lights(data_set, show_severity):
    """
    :param show_severity: Determines whether a user wants to see the severity of the crashes
    :return: A bar graph
    """

    vis_df = data_set.copy()
    vis_df = vis_df[vis_df['dark'] == 1]

    if show_severity == 0:
        vis_df = vis_df.groupby(['number_of_lights'], as_index=False).agg({'cyclists': sum})
        fig = px.bar(
            vis_df,
            x='number_of_lights',
            y='cyclists',
            color_discrete_sequence=colors_list,
            title='Crashes by Street Light Count',
            labels={
                'cyclists': 'Cyclists',
                'severity': 'Severity',
                'number_of_lights': 'Number of Lights',
                'sunset': 'Sunset'
            }
        )
    else:
        vis_df = vis_df.groupby(['number_of_lights', 'severity'], as_index=False).agg({'cyclists': sum})
        fig = px.bar(
            vis_df,
            x='number_of_lights',
            y='cyclists',
            color='severity',
            color_discrete_sequence=colors_list,
            title='Crash Severity by Street Light Count',
            labels={
                'cyclists': 'Cyclists',
                'severity': 'Severity',
                'number_of_lights': 'Number of Lights',
                'sunset': 'Sunset'
            }
        )

    fig = update_fig_layout(fig)

    return fig


@app.callback(
    [
        Output(component_id='crashes_by_sunset_time', component_property='figure'),
        Output(component_id='crashes_by_street_lights', component_property='figure')
    ],
    [
        Input(component_id='bool_show_severity', component_property='value')
    ]
)
def crashes_by_lighting_visuals(show_severity):
    vis_df = df_crash_data[['number_of_lights', 'sunset', 'date', 'time', 'cyclists', 'dark', 'severity']]

    fig_crashes_by_month = crashes_by_month(vis_df)
    fig_crashes_by_street_lighting = crashes_by_street_lights(vis_df, show_severity)

    return fig_crashes_by_month, fig_crashes_by_street_lighting
