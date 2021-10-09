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
        font_size=10,
        title_font_size=14,
        legend_font_size=12
    )

    return fig


