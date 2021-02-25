import numpy as np
import matplotlib.pyplot as plt
from utils import database
import buoy_scraper
import pandas as pd

from timedate import Timedate
import historical_calcs


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
    time = swell_data['Time']

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
    # my assumptions that a 7 ft read on buoy is difference between large and small
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


def percent_trending(wave_height, wave_period):

    percent_change_height = []
    percent_change_period = []

    for i in range(0,len(wave_height) - 1):
        delta = ((wave_height[i] - wave_height[i + 1]) / wave_height[i + 1]) * 100
        percent_change_height.append(delta)

        percent_change_height = list(np.around(np.array(percent_change_height), 2))
    percent_change_height.reverse()

    print(f'Wave Height - 5 hour percentage change (0-5 hours): {percent_change_height[0]}%, (5-10 hours):{percent_change_height[1]}%, (5-10 hours): {percent_change_height[2]}%')

    for i in range(0, len(wave_period) - 1):
        delta_per = ((wave_period[i] - wave_period[i + 1]) / wave_period[i + 1]) * 100
        percent_change_period.append(delta_per)
        percent_change_period = list(np.around(np.array(percent_change_period), 2))
    percent_change_period.reverse()

    print(f'Wave Period - 5 hour percentage change (0-5 hours): {percent_change_period[0]}%, (5-10 hours): {percent_change_period[1]}%, (5-10 hours): {percent_change_period[2]}%')
    return


def wave_power_calculation(wave_height, wave_period): # ADD column? pplot this...?
    # Dominant wave heigth, dominant wave period, other_wave_period is the average period of all waves; assume this is general swell energy for non-dominant waves
    wave_height = list(wave_height)
    wave_period = list(wave_period)

    power = wave_height[0] ** 2
    dom_wave_period = wave_period[0]
    wave_calc = power * dom_wave_period #h^2mo * T
    pascal = .5 # kW / meter cubed * second
    wave_power = pascal * wave_calc
    print(f'The most recent wave power calculation is {round(wave_power,2)}')
    return wave_power


# Average wave period method that can describe the extra wave energy in the water, my hunch is potentially a predictor to combo NW , SW swells
def other_wave_period_assessment(avg_wave_period):
    avg_period_delta = []

    for i in range(0,len(avg_wave_period) - 1):
        delta = ((avg_wave_period[i] - avg_wave_period[i + 1]) / avg_wave_period[i + 1]) * 100
        avg_period_delta.append(delta)

        avg_period_delta = list(np.around(np.array(avg_period_delta), 2))
    avg_period_delta.reverse()

    return avg_period_delta



def menu(): # update menu for daily forecast vs Historical swells.
    user_input = input('To run the program press the any key: ')

    while user_input != 'q':
        user_input = input("""
To get new data enter 'r': 
To see daily trends select 'd': 
To see historical data select 'h': 
To quit program press 'q': 
""").lower()

        if user_input == 'r':
            # scrape data from NOAA
            df = buoy_scraper.scrape_buoy_data()
            # fix columns
            df = buoy_scraper.convert_time_columns(df, Timedate.AMPM)
            # write data to CSV
            buoy_scraper.write_wave_data(df)
            # check if table exists in SQL lite
            database.create_buoy_data()
            # write CSV to SQL
            database.add_buoy_data()

        if user_input == 'd':
            user_input = input(
"""
To view today's data press 'v': 
to view daily trends press 't': 
To quit program press 'q': 
""").lower()

            if user_input == 'v':
                swell_data = buoy_scraper.read_buoy_csv() # update to swell_data pulled from SQL
                print_data(swell_data)
                wave_height, wave_period, avg_period, time = forecast_today(swell_data)
                print(swell_categorisation(wave_height, wave_period))
                wave_power_calculation(wave_height, wave_period)

            if user_input =='t':
                swell_data = buoy_scraper.read_buoy_csv() # update to swell_data pulled from SQL
                wave_height, wave_period, avg_period, time = forecast_today(swell_data)
                raw_day_trends(wave_height, wave_period, avg_period)
                percent_trending(wave_height, wave_period)
                plt.show()

        if user_input == 'h':
            user_input = input(
"""
to view two day trend enter 't': 
To view all historical data enter 'n': 
""").lower()
            if user_input == 't':
                # note if program is not manually refreshed every 23.5 hours data will be innacurate
                #historical_calcs.plot_two_day_wavepower()
                historical_calcs.plot_two_day_trend()


            elif user_input == 'n':
                pass # create plot for all


menu()
