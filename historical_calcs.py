import matplotlib.pyplot as plt
import pandas as pd
from utils import database



def plot_two_day_trend():
    df = database.get_two_days()

    x = [x for x in range(0, 96)]
    y = df['WVHTft']

    y2 = df['DPDsec']
    y3 = df['APDsec']

    plt.xlabel('30 minute interval for last two days')
    plt.ylabel('Wave Height in Feet')

    plt.title('Two Day Trend')

    plt.plot(x, y, label = 'Wave Height ft')
    plt.plot(x, y2, label = 'Dominant Wave Period secs')
    plt.plot(x, y3, label = 'Average Wave Period secs')
    plt.legend()
    plt.show()
    return


def plot_two_day_wavepower():
    df = database.get_two_days()
    

    df['WVHTft'].pow(2).mul(df['DPDsec']).mul(.5).plt()
    return


