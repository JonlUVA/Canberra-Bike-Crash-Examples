# this is a working file where I will export some data for a better view
import openpyxl
import pandas

from cycling_load_data import *

data_index_path = Path(DATA_FOLDER) / DATA_INDEX

working = load_data(data_index_path)

def weather_data_clean(data,weather_station):

    weather_data_frame = data[weather_station].get_data()
    weather_data_frame = weather_data_frame.fillna(0)
    weather_data_frame['date'] = pandas.to_datetime(weather_data_frame['date_time']).dt.date
    return weather_data_frame


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
    weather_data_frame = weather_data_clean(weather, 'canberra airport')
    weather_and_cyclist_date = pandas.merge(cyclist_data, weather_data_frame, on='date', how='left')
    return weather_and_cyclist_date


from suntime import Sun, SunTimeException
from datetime import datetime, time
import numpy
from math import sin, cos, sqrt, atan2, radians


# approximate radius of earth in km


def crash_sun_weather(crash_data, weather):
    """this function takes the cyclist data, and the weather data
    this functions uses the Canberra Airport weather station over the Tuggernong station as the canberra airport station
    is only 8.6km while the tuggernong stations is 18.1km

    :argument  ACT government Bike Barometer - MacArthur Avenue , daily rainfall
    :return a pandas df with the daily sums of cyclists and the daily rainfall.
    """

    crash_data['date'] = pandas.to_datetime(crash_data['date_time']).dt.date
    crash_data['time'] = pandas.to_datetime(crash_data['date_time']).dt.time

    sunset = list()
    sunrise = list()
    closest_weather_station = list()

    for x in crash_data.index:
        sun = Sun(float(crash_data['lat'][x]), float(crash_data['long'][x]))
        sun_ss = datetime.time(sun.get_local_sunset_time(crash_data['date'][x]))
        sun_sr = datetime.time(sun.get_local_sunrise_time(crash_data['date'][x]))
        distance_cbr_air = weather['canberra airport'].distance_from_station(crash_data['lat'][x],
                                                                             crash_data['long'][x])
        distance_tuggeranong = weather['tuggeranong'].distance_from_station(crash_data['lat'][x],
                                                                            crash_data['long'][x])
        sunset.append(sun_ss)
        sunrise.append(sun_sr)
        if distance_cbr_air < distance_tuggeranong:
            closest_weather_station.append("canberra airport")
        else:
            closest_weather_station.append("tuggeranong")

    #remove timezones from date_time
    crash_data['sunset'] = sunset
    crash_data['sunrise'] = sunrise
    crash_data['closest weather station'] = closest_weather_station

    weather_tug = crash_data[crash_data['closest weather station'] == 'tuggeranong']
    weather_cbra = crash_data[crash_data['closest weather station'] == 'canberra airport']
    weather_tug = pandas.merge(weather_tug, weather_data_clean(weather,'tuggeranong'), on="date", how="left")
    weather_cbra = pandas.merge(weather_cbra, weather_data_clean(weather, 'canberra airport'), on="date", how="left")
    crash_weather_df = pandas.concat([weather_cbra, weather_tug], ignore_index=True)
    crash_weather_df['dark'] = numpy.where((crash_weather_df['sunset'] < crash_weather_df['time']) | (crash_weather_df['sunrise'] > crash_weather_df['time']) , 1, 0)
    #crash_weather_df.to_excel(r"C:\Users\Admin\OneDrive\Documents\assignment 2 working\crash_look.xlsx")

    return crash_weather_df


def add_class_suburb(crash_data, suburb):
    """"
    add the suburbs based on long lat and not what the report says
    """
    suburb_list = list()
    lat_long = (crash_data[['lat','long']]).values.tolist()
    def suburb_iter(sub):
        return (suburb.locate(sub[0],sub[1])).get('suburb')
    suburb_list = list(map(suburb_iter, lat_long))
    print(suburb_list)
    #for x in lat_long:
    #    working_suburb_list = (suburb.locate(x[0],x[1])).get('suburb')
    #    print(working_suburb_list)
    #    suburb_list.append(working_suburb_list)

    return


#estimated_cyclist_number_daily_rainfall(working['cyclist'],working['rainfall'])
add_class_suburb((crash_sun_weather(working['crash'], working['rainfall'])), working['suburb'])
