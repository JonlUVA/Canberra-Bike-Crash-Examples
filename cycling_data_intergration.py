# this is a working file where I will export some data for a better view
import openpyxl
import pandas

from cycling_load_data import *

data_index_path = Path(DATA_FOLDER) / DATA_INDEX

working = load_data(data_index_path)


def estimating_cyclist_number(cyclist_data):
    """ this function takes the input given by the 'ACT government Bike Barometer - MacArthur Avenue'
    :argument  ACT government Bike Barometer - MacArthur Avenue
    :return a pandas df with sum's of daily bike usage
    """
    cyclist_data['date'] = pandas.to_datetime(cyclist_data['date_time']).dt.date
    cyclist_data_sum_by_date = cyclist_data.groupby('date')['macarthur_ave_display'].sum()
    cyclist_data_sum_by_date = cyclist_data_sum_by_date.to_frame().reset_index()

    return cyclist_data_sum_by_date


def estimated_cyclist_number_daily_rainfall(cyclist_data, weather):
    """this function takes the cyclist data, and the weather data
    this functions uses the Canberra Airport weather station over the Tuggernong station as the canberra airport station
    is only 8.6km while the tuggernong stations is 18.1km

    :argument  ACT government Bike Barometer - MacArthur Avenue , daily rainfall
    :return a pandas df with the daily sums of cyclists and the daily rainfall.
    """
    cyclist_data = estimating_cyclist_number(cyclist_data)
    weather_data_frame = weather['canberra airport'].get_data()
    weather_data_frame = weather_data_frame.fillna(0)
    weather_data_frame['date'] = pandas.to_datetime(weather_data_frame['date_time']).dt.date
    weather_and_cyclist_date = pandas.merge(cyclist_data, weather_data_frame, on='date', how='left')
    return weather_and_cyclist_date


from suntime import Sun, SunTimeException
from datetime import datetime, time
import numpy
from math import sin, cos, sqrt, atan2, radians


# approximate radius of earth in km


def crash_dusk_shit(crash_data, weather):
    """this function takes the cyclist data, and the weather data
    this functions uses the Canberra Airport weather station over the Tuggernong station as the canberra airport station
    is only 8.6km while the tuggernong stations is 18.1km

    :argument  ACT government Bike Barometer - MacArthur Avenue , daily rainfall
    :return a pandas df with the daily sums of cyclists and the daily rainfall.
    """
    crash_data['date'] = pandas.to_datetime(crash_data['date_time']).dt.date
    # On a special date in your machine's local time zone
    # crash_data['sunset'] = numpy.sqrt(Sun((crash_data['lat']), (crash_data['long'])).get_local_sunset_time())
    sunset = list()
    sunrise = list()
    closest_weather_station = list()
    # approximate radius of earth in km

    for x in crash_data.index:
        sun = Sun(float(crash_data['lat'][x]), float(crash_data['long'][x]))
        sunset.append(sun.get_local_sunset_time(crash_data['date'][x]))
        sunrise.append(sun.get_local_sunrise_time(crash_data['date'][x]))
        distance_cbr_air = weather['canberra airport'].distance_from_station(crash_data['lat'][x],
                                                                             crash_data['long'][x])
        distance_tuggeranong = weather['tuggeranong'].distance_from_station(crash_data['lat'][x],
                                                                            crash_data['long'][x])
        if distance_cbr_air < distance_tuggeranong:
            closest_weather_station.append("canberra airport")
        else:
            closest_weather_station.append("tuggeranong")
    #remove timezones from date_time
    crash_data['sunset'] = pandas.to_datetime(sunset)
    crash_data['sunrise'] = pandas.to_datetime(sunrise)
    crash_data['closest weather station'] = closest_weather_station
    crash_data.to_excel(r"C:\Users\Admin\OneDrive\Documents\assignment 2 working\crash_look.xlsx")
    return


crash_dusk_shit(working['crash'], working['rainfall'])
