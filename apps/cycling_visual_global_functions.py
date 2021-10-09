import os
import pandas as pd

######################################################################
#              RETRIEVING DATASET FROM CYCLING MAIN                  #
######################################################################


def get_data_for_vis(return_both):
    for i in os.listdir('apps/temp_data'):
        if i.startswith('temp_crashes_'):
            crashes_raw_data = pd.read_csv('apps/temp_data/'+i)
        elif i.startswith('temp_cyclists_'):
            cyclist_raw_data = pd.read_csv('apps/temp_data/'+i)

    if return_both == 1:
        return crashes_raw_data, cyclist_raw_data
    else:
        return crashes_raw_data

######################################################################
#                   GLOBAL FUNCTIONS FOR VISUALS                     #
######################################################################


def get_colors():
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
    list_colors = [
        '#003f5c',
        '#2f4b7c',
        '#665191',
        '#a05195',
        '#d45087',
        '#f95d6a',
        '#ff7c43',
        '#ffa600'
    ]

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
        title_font_size=14,
        legend_font_size=12,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(115,120,125,.2)')
    fig.update_xaxes(showgrid=False)

    return fig

    #plot_bgcolor='rgba(0,0,0,0)'


#https://learnui.design/tools/data-color-picker.html#palette