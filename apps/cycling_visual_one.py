import json
import plotly.express as px
import pandas as pd
import csv
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import apps.cycling_visual_global_functions as vis_global_func
from cycling_dashboard_app import app

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

with open('data/geo/features.json') as geojson_filename:
    geojson_file = json.load(geojson_filename)
    geojson_df = pd.DataFrame(geojson_file['features'])
    geojson_df = geojson_df[['geometry', 'properties']]
    ######################################################################
    #                       CREATING DISTRICT MAP                        #
    ######################################################################
    geo_district_shapes_temp = list()
    geo_district_names = list()
    for index, row in geojson_df.iterrows():
        if row['properties'].get('act_loca_5') == 'D':
            geo_district_shapes_temp.append({
                'type': 'Feature',
                'geometry': row['geometry'],
                'id': row['properties'].get('act_loca_2').title()
            })
            geo_district_names.append(row['properties'].get('act_loca_2').title())
    geo_district_shapes = {'type': 'FeatureCollection', 'features': geo_district_shapes_temp}
    geo_district_name_filters = geo_district_names
    geo_district_name_filters.insert(0, 'All')
    ######################################################################
    #                        CREATING SUBURB MAP                         #
    ######################################################################
    geo_suburb_shapes_temp = list()
    geo_suburb_names = list()
    for index, row in geojson_df.iterrows():
        row_properties = row.get('properties')
        if row_properties.get('act_loca_5') == 'G':
            geo_suburb_shapes_temp.append({
                'type': 'Feature',
                'geometry': row.get('geometry'),
                'id': row.get('properties').get('act_loca_2').title()
            })
            geo_suburb_names.append(row.get('properties').get('act_loca_2').title())
    geo_suburb_shapes = {'type': 'FeatureCollection', 'features': geo_suburb_shapes_temp}
    geo_suburb_names.insert(0, 'All')
geojson_filename.close()

######################################################################
#                        RETRIEVING TEMP DATA                        #
######################################################################

crashes_df = vis_global_func.get_data_for_vis(0)

"""
https://aesalazar.com/blog/professional-color-combinations-for-dashboards-or-mobile-bi-applications
 #B3C100, #CED2CC, #23282D, #4CB5F5, #1F3F49, #D32D41, #6AB187
"""

######################################################################
#                          SETTING UP HTML                           #
######################################################################

var_dashboard = html.Div([
    html.H1(children='Dashboard'),
    html.Div(id='total_number_of_crashes'),
    html.Div(
        id='visuals_parent_wrapper',
        children=[
            html.Div(
                id='map_visual',
                children=[
                    html.Div(
                        children=[
                            html.H3(
                                children='Select a Granularity'
                            ),
                            dcc.RadioItems(
                                id='selected_map_granularity',
                                options=[
                                    {
                                        'value': 'Suburbs',
                                        'label': 'Suburbs'
                                    },
                                    {
                                        'value': 'Districts',
                                        'label': 'Districts'
                                    }
                                ],
                                value='Districts',
                                labelStyle={'display': 'block'},
                            )
                        ]
                    ),
                    html.Div(
                        children=[
                            dcc.Graph(id='crash_map'),
                            dcc.Slider(
                                id='selected_year',
                                min=2012,
                                max=2021,
                                value=2021,
                                marks={
                                    2012: '2012', 2013: '2013', 2014: '2014',
                                    2015: '2015', 2016: '2016', 2017: '2017',
                                    2018: '2018', 2019: '2019', 2020: '2020',
                                    2021: 'All'
                                },
                                step=None
                            )
                        ],
                    )
                ],
            ),
            html.Div(
                id='wrapper_supplementary_visuals',
                children=[
                    dcc.Dropdown(
                        id='location_filter',
                        options=[{'label': i, 'value': i} for i in geo_district_name_filters],
                        multi=False,
                        value='All'
                    ),
                    dcc.Graph(id='location_crash_count_by_year'),
                    dcc.Graph(id='location_crash_severity_by_year')
                ]
            )
        ],
    )
])

#########################################
#          GENERATING VISUALS           #
#########################################

@app.callback(
    [
        Output(component_id='crash_map', component_property='figure'),
        Output(component_id='total_number_of_crashes', component_property='children')
    ],
    [
        Input(component_id='selected_year', component_property='value'),
        Input(component_id='selected_map_granularity', component_property='value'),
        Input(component_id='crash_map', component_property='clickData')
    ]
)
def map_crashes_by_suburb_and_date(selected_year, selected_map_granularity, click_data):
    #https://www.justintodata.com/python-interactive-dashboard-with-plotly-dash-tutorial/
    #https://python.plainenglish.io/how-to-create-a-interative-map-using-plotly-express-geojson-to-brazil-in-python-fb5527ae38fc
    #https://towardsdatascience.com/choropleth-maps-in-practice-with-plotly-and-python-672a5eef3a19
    """
    :param selected_year: year selected by a user via slider component
    :param selected_map_granularity: map granularity selected by user via radio buttons
    :param click_data: map data returned from when user clicks on map visual
    :return: map visual and sum of all crashes in act for given time period
    """

    #   GETTING THE LOCATION FROM MAP CLICK DATA
    if click_data != None:
        print(click_data.get('points')[0].get('location'))

    #   SETTING VARIABLES FOR MAP VISUAL
    if selected_map_granularity == 'Districts':
        var_geojson = geo_district_shapes
        var_location = 'district'
        var_all_locations_list = geo_district_names
        var_zoom = 8.25
        var_center = {'lat': -35.51405, 'lon': 149.07130}
    elif selected_map_granularity == 'Suburbs':
        var_geojson = geo_suburb_shapes
        var_location = 'suburb'
        var_all_locations_list = geo_suburb_names
        var_zoom = 9.25
        var_center = {'lat': -35.3222, 'lon': 149.1287}

    #   2021 = ALL YEARS
    if selected_year == 2021:
        selected_year_crash_data = crashes_df[['date', var_location, 'cyclists']]
    else:
        selected_year_crash_data = crashes_df.loc[
            pd.to_datetime(crashes_df['date']).dt.year == selected_year, [var_location, 'cyclists']]

    selected_year_crash_data_df = selected_year_crash_data.groupby(
        [var_location], as_index=False).agg({'cyclists': sum})

    #   IF ANY LOCATION HAS NO DATA LOCATION WILL = 0
    for i in var_all_locations_list:
        if selected_year_crash_data_df[selected_year_crash_data_df[var_location] == i].empty:
            selected_year_crash_data_df = selected_year_crash_data_df.append(
                {var_location: i, 'cyclists': 0}, ignore_index=True)

    sum(selected_year_crash_data_df['cyclists'])
    max_colour = max(selected_year_crash_data_df['cyclists'])

    var_total_crash_count = [html.H2(
        children='Total number of crashes for '
                 + str(selected_year)
                 + ': '
                 + str(sum(selected_year_crash_data_df['cyclists']))
    )]

    fig = px.choropleth_mapbox(
        selected_year_crash_data_df,
        geojson=var_geojson,
        locations=var_location,
        color="cyclists",
        color_continuous_scale=[
            '#665191',
            '#a05195',
            '#d45087',
            '#f95d6a',
            '#ff7c43',
            '#ffa600'
        ],
        title='map test ' + str(selected_year),
        mapbox_style='carto-darkmatter',
        zoom=var_zoom,
        center=var_center,
        opacity=0.5,
        range_color=(0, max_colour)
    )

    fig.update_layout(
        margin=dict(
            b=0,
            l=0,
            r=0,
            t=0
        ),
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig, var_total_crash_count


def crashes_count_by_location_and_year(data_set, location):
    vis_df = data_set.drop(columns=['severity'])
    vis_df = vis_df.groupby(['year'], as_index=False).agg({'cyclists': sum})

    fig = px.line(
        vis_df,
        x='year',
        y='cyclists',
        title=location + '\'s Cyclist Crashes by Year',
        labels={
            'year': 'Year',
            'cyclists': 'Cyclists'
        }
    )

    fig = vis_global_func.update_fig_layout(fig)

    return fig


def crash_severity_by_location_and_year(data_set, location):
    vis_df = data_set.groupby(['year', 'severity'], as_index=False).agg({'cyclists': sum})
    fig = px.bar(
        vis_df,
        x='year',
        y='cyclists',
        color='severity',
        title=location + '\'s Cyclist Crashes by Year and Severity',
        labels={
            'year': 'Year',
            'cyclists': 'Cyclists',
            'severity': 'Severity'
        },
        barmode='group',
        log_y=True
    )

    fig = vis_global_func.update_fig_layout(fig)

    return fig


@app.callback(
    [
        Output(component_id='location_crash_count_by_year', component_property='figure'),
        Output(component_id='location_crash_severity_by_year', component_property='figure')
    ],
    [
        Input(component_id='selected_map_granularity', component_property='value'),
        Input(component_id='location_filter', component_property='value')
    ]
)
def location_crash_count_visuals(selected_map_granularity, location_filter_value):

    #   DETERMINING WHAT DATA TO PULL
    if selected_map_granularity == 'Suburbs':
        location_type = 'suburb'
    elif selected_map_granularity == 'Districts':
        location_type = 'district'

    #############################
    #   GETTING REQUIRED DATA   #
    #############################

    vis_df = crashes_df
    #   SELECTING COLUMNS
    vis_df = vis_df[[location_type, 'cyclists', 'severity', 'date']]
    #   ADDING YEAR COLUMN
    vis_df_year = vis_df.copy()
    vis_df_year['year'] = pd.DatetimeIndex(vis_df['date']).year
    #   DROPPING DATE COLUMN
    vis_df_year = vis_df_year.drop(columns=['date'])
    #   FILTERING LOCATION
    if location_filter_value != 'All':
        vis_df_year = vis_df_year.loc[vis_df_year[location_type] == location_filter_value]
    else:
        pass
    vis_df_year = vis_df_year.drop(columns=[location_type])

    #   MAKING THE TITLES OF VISUAL SHOW CANBERRA INSTEAD OF ALL
    if location_filter_value == 'All':
        location = 'ACT'
    else:
        location = location_filter_value

    #   CREATING THE VISUALS
    fig_crash_count = crashes_count_by_location_and_year(vis_df_year, location)
    fig_crash_severity = crash_severity_by_location_and_year(vis_df_year, location)

    return fig_crash_count, fig_crash_severity


@app.callback(
    [
        Output(component_id='location_filter', component_property='options'),
        Output(component_id='location_filter', component_property='value')
    ],
    [
        Input(component_id='selected_map_granularity', component_property='value'),
        Input(component_id='crash_map', component_property='clickData')
    ]
)
def update_location_filter_dropdown(selected_map_granularity, click_data):
    if selected_map_granularity == 'Suburbs':
        selected_options = [{'label': i, 'value': i} for i in geo_suburb_names]
    elif selected_map_granularity == 'Districts':
        selected_options = [{'label': i, 'value': i} for i in geo_district_name_filters]

    if click_data != None:
        selected_location = click_data.get('points')[0].get('location')
    else:
        selected_location = 'All'

    return selected_options, selected_location
