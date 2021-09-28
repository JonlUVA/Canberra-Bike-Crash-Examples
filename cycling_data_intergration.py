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
    weather = weather['canberra airport'].get_data()
    weather = weather.fillna(0)
    weather['date'] = pandas.to_datetime(weather['date_time']).dt.date
    weather_and_cyclist_date = pandas.merge(cyclist_data, weather, on='date', how='left')
    return weather_and_cyclist_date





estimated_cyclist_number_daily_rainfall(working['cyclist'], working['rainfall'])

