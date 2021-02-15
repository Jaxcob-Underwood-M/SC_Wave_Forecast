import numpy as np
import matplotlib.pyplot as plt
from utils import database
import buoy_scraper
import pandas as pd

#write method to append data to POSTGRE SQL
#Either write method to remove duplicate rows based on date / hour, or to automatically scrape every hour



#write method to pull recent data, 1 day or 2 days

def print_data(swell_data):
    print(swell_data)
    return

#five hour average method will iterate over all the rows in the columns
def five_hour_average(column):
    avg = []
    tmp = []
    iter = 0
    it = 0
    for i in range(0,len(column)):
        tmp.append(column[i])
        if iter == 9:
            avg.append(np.average(tmp))
            it += 1
            tmp = []
            iter = 0
        elif i == len(column):
            avg.append(np.average(tmp))
        iter += 1
    return avg

def plot_data(wave_height, wave_period, avg_period, time):
    wh = np.flip(pd.Series.to_numpy(wave_height))
    wp = np.flip(pd.Series.to_numpy(wave_period))
    ap = np.flip(pd.Series.to_numpy(avg_period))
    t = np.flip(pd.Series.to_numpy(time))
    fig, (ax1,ax2,ax3) = plt.subplots(3, 1)
    fig.suptitle('Daily Forecast for Stoke')
    ax1.plot(wh)
    ax1.set(ylabel = 'Wave Height')
    ax2.plot(wp)
    ax2.set(ylabel='Wave Period')
    ax3.plot(ap)
    ax3.set(ylabel='Average Period')


def forecast_today(swell_data):
    wave_height = swell_data['WVHTft']
    dominant_wave_period = swell_data['DPDsec']
    average_wave_period = swell_data['APDsec']
    wave_direction = swell_data['MWD'][0:9]
    time = swell_data['TIMEpst'] # will need to change this column name when the SQL connection is completed

    plot_data(wave_height, dominant_wave_period, average_wave_period, time)
    # five hour averages
    wave_height_avg = five_hour_average(wave_height)
    dom_wave_avg = five_hour_average(dominant_wave_period)
    ave_wave_avg = five_hour_average(average_wave_period)

    # get rounded values
    rounded_wave_height_avg = list(np.around(np.array(wave_height_avg),2))
    rounded_dom_wave_avg = list(np.around(np.array(dom_wave_avg),2))
    rounded_ave_wave_avg = list(np.around(np.array(ave_wave_avg),2))

    print(f'5 hr average wave height is {rounded_wave_height_avg[0]} ft from {wave_direction[0]} | {wave_direction[1]}')
    print(f'5 hr average dominant period is {rounded_dom_wave_avg[0]} seconds')
    print(f'5 hr average average period is {rounded_ave_wave_avg[0]} seconds')

    return rounded_wave_height_avg, rounded_dom_wave_avg, rounded_ave_wave_avg, time

def swell_categorisation(wave_height, wave_period):
    # my assumptions that a period over 15 seconds assumes waves traveled a long distance
    # my assumptions that a 7 ft read on buoy is difference between big and small
    PERIOD = 15
    HEIGHT = 7

    #take most recent average of the list of averages
    wave_height = wave_height[0]
    wave_period = wave_period[0]

    # groundswell or windswell
    if wave_period > PERIOD:
        if wave_height > HEIGHT:
            return 'Large Groundswell'
        elif wave_height <= HEIGHT:
            return 'Small Groundswell'
    elif wave_period <= PERIOD:
        if wave_height > HEIGHT:
            return 'Large Windswell'
        else:
            return 'Small Windswell'


def raw_day_trends(wave_height, wave_period, avg_wave_period):
    #daily change
    last_iter_height = int(len(wave_height))
    last_iter_period = int(len(wave_period))
    last_iter_avgperiod = int(len(avg_wave_period))

    delta_height = round(wave_height[0] - wave_height[last_iter_height - 1], 2)
    delta_period = round(wave_period[0] - wave_period[last_iter_period - 1], 2)
    delta_avg_period = round(wave_height[0] - avg_wave_period[last_iter_avgperiod - 1], 2)


    print(f'24 hour delta of dominant height {delta_height} ft')
    print(f'24 hour delta of dominant period is {delta_period} seconds')
    print(f'24 hour delta of average wave period {delta_avg_period} seconds')
    return


def percent_trending(wave_height, wave_period, avg_wave_period):

    percent_change_height = []

    for i in range(0,len(wave_height) - 1):
        delta = ((wave_height[i] - wave_height[i + 1]) / wave_height[i + 1]) * 100
        percent_change_height.append(delta)

        percent_change_height = list(np.around(np.array(percent_change_height),2))
        percent_change_height.reverse()
    # I NEED TO PRINT THIS IN A PRETTY WAY
    print(f'5 Hour {percent_change_height[0]}%, 10 Hour %{percent_change_height[1]}%, 15 Hour {percent_change_height[2]}%')
    return


def wave_power_calculation(wave_height, wave_period, other_wave_period):
    # will return a non-dimension unit
    # Dominant wave heigth, dominant wave period, other_wave_period is the average period of all waves; assume this is general swell energy for non-dominant waves
    density_salt_water = 1020 # kilogram / m^3
    power = wave_height ^ 5
    buoy_ocean_depth = 65 # feet

    dom_wave_period = wave_period
    non_dominant_wave_period = other_wave_period


def menu():
    user_input = input('To run the program press the key "yes": ')
    while user_input != 'q':
        user_input = input(
"""
To refresh data press 'r'
To view todays data press 'v'
to view daily trends press 't'
To quit program press 'q'
""")
        if user_input == 'r':
            # scrape data from NOAA
            df = buoy_scraper.scrape_buoy_data()
            # write data to CSV
            buoy_scraper.write_wave_data(df)
            # check if table exists
            database.create_buoy_data()
            # write CSV to SQL
            database.add_buoy_data()
        if user_input == 'v':
            # this will be updated to pull data from SQL
            swell_data = buoy_scraper.read_buoy_csv()
            wave_height, wave_period, avg_period, time = forecast_today(swell_data)
            print(swell_categorisation(wave_height, wave_period))
        if user_input =='t':
            # this will be updated to pull data from SQL
            swell_data = buoy_scraper.read_buoy_csv()
            wave_height, wave_period, avg_period, time = forecast_today(swell_data)
            raw_day_trends(wave_height, wave_period, avg_period)
            percent_trending(wave_height, wave_period, avg_period)

            plt.show()



menu()



