# this is a working file where I will export some data for a better view

import pandas

from cycling_load_data import *
from suntime import Sun
from datetime import datetime
import numpy
from math import sin, cos, sqrt, asin, radians




def weather_data_clean(data, weather_station):
    """" this function reads the weather class structure and returns a dataframe.
    :argument weather class data, name of station
    :return dataframe with weather station data

    """
    weather_data_frame = data[weather_station].get_data()
    # changing na to zeros to reduce missing values
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

def sum_of_daily_crashes(crash_data):
    """This function takes the ACT cyclist Crash data and returns a dataframe with the date (dd/mm/yyyy) and the sum
    of crashes
    :argument ACT cyclist Crash Data
    :return pandas df with sum of daily bike crash
    """
    crash_data['date'] = crash_data['date_time'].dt.date
    value_counts = crash_data['date'].value_counts(dropna=True, sort=True)
    value_counts = pd.DataFrame(value_counts)
    value_counts = value_counts.reset_index()
    value_counts.columns = ['date', 'daily_crash_count']
    return value_counts


def estimated_cyclist_number_daily_rainfall_crash_number(cyclist_data, weather, crash_data):
    """this function takes the cyclist data, and the weather data
    this functions uses the Canberra Airport weather station over the Tuggernong station as the canberra airport station
    is only 8.6km while the tuggernong stations is 18.1km

    :argument  ACT government Bike Barometer - MacArthur Avenue , daily rainfall
    :return a pandas df with the daily sums of cyclists and the daily rainfall.
    """

    cyclist_data = estimating_cyclist_number(cyclist_data)
    weather_data_frame = weather_data_clean(weather, 'canberra airport')
    crash_sums = sum_of_daily_crashes(crash_data)
    # left join was chosen as there may be missing values
    weather_and_cyclist_date = pandas.merge(cyclist_data, weather_data_frame, on='date', how='left')
    weather_and_cyclist_date_crash = pandas.merge(weather_and_cyclist_date, crash_sums, on='date', how='left')
    weather_and_cyclist_date_crash['daily_crash_count'] = weather_and_cyclist_date_crash['daily_crash_count'].fillna(0)
    weather_and_cyclist_date_crash.to_excel(r"C:\Users\Admin\OneDrive\Documents\assignment 2 working\crash.xlsx")
    return weather_and_cyclist_date_crash


def crash_sun_weather(crash_data, weather):
    """this function takes the cyclist data, and the weather data
    this functions uses the Canberra Airport weather station over the Tuggernong station as the canberra airport station
    is only 8.6km while the tuggernong stations is 18.1km

    :argument  ACT government Bike Barometer - MacArthur Avenue , daily rainfall
    :return a pandas df with the daily sums of cyclists and the daily rainfall.
    """
    # creating time_Data to 2 values, time and date
    crash_data['date'] = pandas.to_datetime(crash_data['date_time']).dt.date
    crash_data['time'] = pandas.to_datetime(crash_data['date_time']).dt.time

    sunset = list()
    sunrise = list()
    closest_weather_station = list()
    # calculating the distance each crash is from each weather station to determine which one is closest
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

    crash_data['sunset'] = sunset
    crash_data['sunrise'] = sunrise
    crash_data['closest weather station'] = closest_weather_station
    # creating two dataframes and adding the weather information to the date and crash information
    weather_tug = crash_data[crash_data['closest weather station'] == 'tuggeranong']
    weather_cbra = crash_data[crash_data['closest weather station'] == 'canberra airport']
    weather_tug = pandas.merge(weather_tug, weather_data_clean(weather, 'tuggeranong'), on="date", how="left")
    weather_cbra = pandas.merge(weather_cbra, weather_data_clean(weather, 'canberra airport'), on="date", how="left")
    crash_weather_df = pandas.concat([weather_cbra, weather_tug], ignore_index=True)
    # creating a binary indicator to whether it is dark or not. this has been
    # caclulated that is is dark exactly after sunset and only before sunrise.
    # this was done to reduce the number of street lights we need to calcuated
    crash_weather_df['dark'] = numpy.where((crash_weather_df['sunset'] < crash_weather_df['time']) | (
            crash_weather_df['sunrise'] > crash_weather_df['time']), 1, 0)
    return crash_weather_df


def add_class_suburb(crash_data, suburb):
    """"
    add the suburbs based on long lat and not what the report says
    """
    lat_long = (crash_data[['lat', 'long']]).values.tolist()
    def suburb_iter(data):
        """"used for getting the suburb by the geolocation as defined in suburb class
        faster than a traditional loop"""
        return list(suburb.locate(data[0], data[1]).values())
    # using a map function over a loop as its faster
    suburb_list = [item for sublist in (list(map(suburb_iter, lat_long))) for item in sublist]
    crash_data['suburb'] = suburb_list[::2]
    crash_data['district'] = suburb_list[1::2]
    # if there is no suburb information take the district
    #crash_data.loc[crash_data['suburb'] == '', 'suburb'] = crash_data['district']
    crash_data.loc[crash_data['suburb'] == '', 'suburb'] = "NA"
    return crash_data


def lights_final(crash, rain, suburb, lights):
    """"
    This function takes the crash, rainfall, suburb, and street light data
    and returns a final product dataframe which contains all bike crash data with their daily rainfall,
    which suburb they are in, and if it is dark how many street lights were within 30 meters
    :argument bike-crash data, rainfall data, suburb class, street light data
    :return single dataframe containing crash, streetlight, rainfall and suburb class data
    """
    crash_final = add_class_suburb((crash_sun_weather(crash, rain)), suburb)
    crash_final_dark = crash_final[crash_final['dark'] == 1]
    dark_lat_long_list = (crash_final_dark[['lat', 'long', 'crash_id']]).values.tolist()
    light_list = (lights[['lat', 'long']]).values.tolist()

    R = 6371  # km
    crash_dict = dict()

    for x in dark_lat_long_list:
        count = 0
        for y in light_list:
            dLat = radians(y[0] - x[0])
            dLon = radians(y[1] - x[1])
            lat1 = radians(x[0])
            lat2 = radians(y[0])
            a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
            c = 2 * asin(sqrt(a))
            distance = R * c
            if distance < 0.03: # 0.03 = 30 meters
                count += 1
        crash_dict[int(x[2])] = count

    crash_lights = pandas.DataFrame(list(crash_dict.items()), columns=['crash_id', 'number_of_lights'])
    crash_final = (crash_final.merge(crash_lights, on='crash_id', how='left')).fillna(-1)
    return crash_final



# they're used in main to check for local data dump files to improve efficiency
# on subsequent executions
def integration(data):
    """" this is the final function, calling this will return a dictionary containing two dataframes,
    1 the estimated cyclist data and two the bike crash data
    """
    data_integration_dic = dict()
    data_integration_dic['cyclists'] = estimated_cyclist_number_daily_rainfall_crash_number(data['cyclist'], data['rainfall'], data['crash'])
    data_integration_dic['crashes'] = lights_final(data['crash'], data['rainfall'], data['suburb'], data['streetlight'])

    return data_integration_dic


# below code is used for testing purposes.
if __name__ == '__main__':
    data_index_path = Path(DATA_FOLDER) / DATA_INDEX
    working = load_data(data_index_path)
    
    from datetime import datetime
    start_time = datetime.now()
    
    print(integration(working))
    end_time = datetime.now()
    duration = end_time - start_time
    print(f'running time: {duration}')