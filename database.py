import csv
import sqlite3 as sq
import pandas as pd

from .database_connection import DatabaseConnection

def create_buoy_data():
    connection = sq.connect('Swell.db')
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS wave_data (MM text, DD text, TIMEpst text, WVHTft real, DPDsec real, APDsec real, MWD TEXT)')
    connection.commit()
    print(connection.total_changes)
    connection.close()


def add_buoy_data(): # create a method that can be called after data = pd.read_csv that concatenates MM, DD, TIMEpst. the concatenated column will be the DISTINCT SERIAL
    # will also need to add another column into the execute line
    with DatabaseConnection('swell.db') as connection:
        cursor = connection.cursor()
        data = pd.read_csv('buoy_data.csv')
        #concatenate method
        for i in range(1, len(data)):
            cursor.execute(f"INSERT INTO wave_data VALUES(?,?,?,?,?,?,?)", (str(data['MM'][i]), data['DD'][i], data['TIMEpst'][i], data['WVHTft'][i], data['DPDsec'][i], data['APDsec'][i], data['MWD'][i]))
            print(connection.total_changes)


    # MM, DD, TIMEpst, WVHTft, DPDsec, APDsec, MWD = data['MM'][i],data['DD'][i],data['TIMEpst'][i],\
    #                                                    data['WVHft'][i],data['DPDsec'][i], data['APDsec'][i],data['MWD'][i]
    # cursor.execute(f"INSERT INTO swell_data (?,?,?,?,?,?,?) VALUES ({MM}, {DD}, {TIMEpst}, {WVHTft}, {DPDsec}, {APDsec}, {MWD})")
    # data.to_sql('data', connection, if_exists= 'append', index=False)
    # df = pd.DataFrame(data, columns = ['MM', 'DD', 'TIMEpst', 'WVHTft', 'DPDsec', 'APDsec', 'MWD'])
    # connection = sq.connect('Swell.db')
    # cursor = connection.cursor()
    # cursor.execute()

    # with DatabaseConnection('data.db') as connection:
    #     cursor = connection.cursor()
    #     cursor.executemany(f"INSERT INTO swell_data (MM, DD, TIMEpst, WVHTft, DPDsec, APDsec, MWD) VALUES (?, ?, ?, ?, ?, ?, ?)", to_db)
    return

