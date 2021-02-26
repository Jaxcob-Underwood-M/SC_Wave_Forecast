import sqlite3 as sq
import pandas as pd

from .database_connection import DatabaseConnection

def create_buoy_data():
    with DatabaseConnection('swell.db') as connection:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS wave_data (MM text, DD text, TIMEpst text, WVHTft real, DPDsec real, APDsec real, MWD TEXT, Time text PRIMARY KEY)')


def add_buoy_data(): # create a method that can be called after data = pd.read_csv that concatenates MM, DD, TIMEpst. the concatenated column will be the UNIQUE

    with DatabaseConnection('swell.db') as connection:
        cursor = connection.cursor()
        data = pd.read_csv('buoy_data.csv')
        #concatenate method
        for i in range(1, len(data)):
            cursor.execute(f"INSERT OR IGNORE INTO wave_data VALUES(?,?,?,?,?,?,?,?)", (str(data['MM'][i]), str(data['DD'][i]), data['TIMEpst'][i], data['WVHTft'][i], data['DPDsec'][i], data['APDsec'][i], data['MWD'][i], data['Time'][i]))
        print(f'total new rows entered {connection.total_changes}')
    return


def get_all_historical_data():
    with DatabaseConnection('swell.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM wave_data ORDER BY Time') # appears order by is limited to one
        swell_data = cursor.fetchall()

    swell_data = pd.DataFrame(swell_data, columns =['MM', 'DD', 'TIMEpst', 'WVHTft', 'DPDsec', 'APDsec', 'MWD', 'Time'])

    return swell_data

def get_two_days():
    with DatabaseConnection('swell.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM wave_data ORDER BY Time DESC Limit 96')
        swell_data = cursor.fetchall()

    swell_data = pd.DataFrame(swell_data, columns =['MM', 'DD', 'TIMEpst', 'WVHTft', 'DPDsec', 'APDsec', 'MWD', 'Time'])

    return swell_data
