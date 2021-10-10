import os
import pandas as pd

######################################################################
#              RETRIEVING DATASET FROM CYCLING MAIN                  #
######################################################################


def get_data_for_vis(return_both):
    """
    :param return_both: Are both cyclist and crashes data required for the vis 0 = no, 1 = yes
    :return: the dataset(s) required
    """
    crashes_raw_data = pd.read_csv('data/crashes.csv')
    cyclist_raw_data = pd.read_csv('data/cyclists.csv')

    if return_both == 1:
        return crashes_raw_data, cyclist_raw_data
    else:
        return crashes_raw_data

######################################################################
#                   GLOBAL FUNCTIONS FOR VISUALS                     #
######################################################################
def get_colors():
    """
    :return: A colour list for use in the visuals
    """
    colors_list = [
        '#003f5c',
        '#2f4b7c',
        '#665191',
        '#a05195',
        '#d45087',
        '#f95d6a',
        '#ff7c43',
        '#ffa600'
    ]

    return colors_list


def update_fig_layout(fig):
    """
        FUNCTION USED TO MAKE VISUALS LOOK SIMILAR IN STYLING
    """
    fig = fig

    fig.update_layout(
        margin=dict(
            b=10,
            l=5,
            r=5,
            t=50,
        ),
        font_color='#73787D',
        font_size=10,
        title_font_size=18,
        legend_font_size=12,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        #autosize=False
    )

    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(115,120,125,.2)')
    fig.update_xaxes(showgrid=False)

    return fig
