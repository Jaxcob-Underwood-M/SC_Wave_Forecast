import requests
import lxml.html as lh
import pandas as pd
import numpy as np

from timedate import Timedate


def scrape_buoy_data():
    url = 'https://www.ndbc.noaa.gov/station_page.php?station=46269'
    page = requests.get(url)
    doc = lh.fromstring(page.content)

    # parse the data stored between the <tr> .. </tr>
    tr_elements = doc.xpath('//tr')

    data_table = []
    # check which row contains headers. Row 18
    for T in tr_elements:
        if len(T) == 18:
            data_table.append(T)
    # create empty list
    col = []
    i = 0

    # create column headers
    for t in data_table[1]:
        i += 1
        name = t.text_content()
        # print('%d:"%s"'%(i,name))
        col.append((name, []))

    # create column data
    for j in range(2, len(data_table)):
        # T is the j'th row
        T = data_table[j]

        if len(T) != 18:
            print('row is not 18')
            break
        # i is index of column
        i = 0
        # iterate through each element of the row
        for t in T.iterchildren():
            data = t.text_content()
            if i > 0:
                try:
                    data = float(data)
                except:
                    pass
            col[i][1].append(data)
            i += 1
    # print([len(C)for (title, C) in col])

    # create dict data frame
    Dict = {title: column for (title, column) in col}
    df = pd.DataFrame(Dict)

    # get pertinent columns
    df = df[['MM', 'DD', 'TIME(PST)', 'WVHTft', 'DPDsec', 'APDsec', 'MWD']]
    # change time column name
    df.columns = ['MM', 'DD', 'TIMEpst', 'WVHTft', 'DPDsec', 'APDsec', 'MWD']

    # replace '-' values with forward looking data
    df = df.replace('-', method= 'ffill')

    # convert columns to correct data types
    df['MM'] = df['MM'].astype(str)
    df['DD'] = df['DD'].astype(str)
    df['DD'] = df['DD'].str.split('.', n=1, expand=True)

    df['TIMEpst'] = df['TIMEpst'].astype(str)

    df['WVHTft'] = df['WVHTft'].astype(str).astype(float)
    df['APDsec'] = df['APDsec'].astype(str).astype(float)
    df['MWD'] = df['MWD'].astype(str)

    # concatenate time columns
    df = convert_time_columns(df, Timedate.AMPM)
    return df


def convert_time_columns(df, AMPM):
    YEAR = '2021'

    time_pst = df['TIMEpst'].values.astype(str).tolist()

    out_time = []
    for i in time_pst:
        i = i[0:5]+' '+i[6:]
        for t in AMPM:
            if i == t:
                i = AMPM[t]
                out_time.append(i)

    # concatenate time variables to create working time series
    df['hour'] = pd.DataFrame(out_time)
    df['Time'] = YEAR + df['MM'].astype(str) + df['DD'].astype(str) + df['hour'].astype(str)

    del df['hour']

    return df


def write_wave_data(df):
    df.to_csv('Buoy_data.csv', index=False)
    return


def read_buoy_csv():
    swell_data = pd.read_csv('Buoy_data.csv')
    return swell_data


def print_data(swell_data):
    print(swell_data)
    return
