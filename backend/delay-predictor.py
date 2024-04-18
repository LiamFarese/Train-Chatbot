
# imports #

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
from pandas.core.interchange import dataframe

from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression, BayesianRidge
from sklearn.metrics import balanced_accuracy_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

import datetime as dt


# constants #

historical_data_path = 'historical-data'
historical_table_path = f'{historical_data_path}/historical_table.csv'


# functions #

# obtains historical data as a pandas dataset
def get_historical_data(year, month):

    month_string = f'{month}'

    # if below 10, will appear in the string as e.g. '_02_02'
    if month < 10:

       month_string = f'0{month}'


    data = pd.read_csv(

        historical_data_path
        + f'/{year}'
        + f'/LIVST_NRCH_OD_a51_{year}_{month_string}_{month_string}.csv'
    )

    return data


# for extracting times from a string of the format 00:00 or 00:00:00 to seconds
def extract_time_to_seconds(time_string):

    # if 00:00 format
    if len(time_string) == 5:

        return (
                # extract hours
                int(time_string[0:2]) * 3600
                # extract minutes
                + int(time_string[3:5]) * 60)

    # if 00:00:00 format
    elif  len(time_string) == 6:

        return (
                # extract hours
                int(time_string[0:2]) * 3600
                # extract minutes
                + int(time_string[3:5]) * 60
                # extract seconds
                + int(time_string[6:8]))

    return None


# extracts the day from the historical data
def extract_date_from_rid(rid_string):

    year = int(rid_string[0:4])
    month = int(rid_string[4:6])
    day = int(rid_string[6:8])

    return year, month, day


# extract and save the full dataset from the historical data
# into a table with columns month, day, day_of_week, duration, delay
def get_full_historical_dataset(print_progress=False):

    data = pd.DataFrame(columns=['delay', 'day', 'duration'])

    for year in range(2022, 2023):

        print(f"Processing year: {year}...")

        for month in range(1, 13):

            if print_progress:

                print(f"\tProcessing month: {month}...")


            historical = get_historical_data(year, month)

            # filtered out where needed columns are not empty
            hist_filtered = (

                historical)[

                    (historical['pta'].notnull())
                    & (historical['arr_at'].notnull())
                    & (historical['ptd'].notnull())
                ]

            first_station_departure = None

            for index, row in hist_filtered.iterrows():


                if first_station_departure is None:

                    first_station_departure = extract_time_to_seconds(row['ptd'])
                    continue


                # extract times to values
                arr_at = extract_time_to_seconds(str(row['arr_at']))
                pta = extract_time_to_seconds(str(row['pta']))


                # planned duration = arrival of current - departure of previous
                duration = pta - first_station_departure

                # if the duration is below 0, do not put in the graph
                if duration <= 0:

                    first_station_departure = extract_time_to_seconds(row['ptd'])
                    continue


                # extract delay, if negative just set to 0
                delay = max(arr_at - pta, 0)

                # do not append if there is no delay
                if delay == 0 or delay is None:

                    continue


                y, m, d = extract_date_from_rid(str(row['rid']))

                date = dt.datetime(y, m, d)

                day = int(date.timetuple().tm_yday)

                if day is None:

                    continue


                # if the delay is over 0, there has been delay
                new_row = {

                    'delay':    delay,
                    'day':      day,
                    'duration': duration}


                data = data._append(new_row, ignore_index=True)


    return data


def train_model(data, model):

    d = data.loc[data['delay'] < 20000]

    X = d[data.columns.drop('delay')]
    y = d['delay']

    print(X)

    seed = 91
    test_size = 0.1

    X_train, X_test, y_train, y_test = train_test_split(
       X, y, test_size=test_size, random_state=seed)

    model.fit(X_train, y_train)
    y_predict = model.predict(X_test)

    plt.scatter(X_train['duration'], y_train, color='black', label='training data')
    plt.plot(X_test['duration'], y_predict, color='b', label='Linear Regression')
    plt.show()


# main #

def main():

    data = None
    option = 1

    while option > 0:

        option = int(input(
            "Select an option:\n"
            "0. Exit\n"
            "1. Full\n"
            "2. Extract table\n"
            "3. Train model\n"
            "9. Extract Graph\n"
            "Your Answer: "))


        full = option == 1


        if full or option == 2:

            data = get_full_historical_dataset(True)
            data.to_csv(historical_table_path)
            print("table saved!\n")


        # all options after 2 require the table to be loaded
        if full or option > 2:

            if data is None:

                data = pd.read_csv(historical_table_path, index_col=0)


        if full or option == 3:

            model = BayesianRidge()

            train_model(data, model)


        if option == 1 or option == 9:

            num_of_points = 12
            divisor = 356 / num_of_points
            averages = []

            for i in range(0, num_of_points):

                r = data.loc[
                    (data['day'] < (i + 1) * divisor)
                    & (data['day'] > i * divisor)]['delay']

                averages.append(r.mean())


            plt.plot(range(0, num_of_points), averages, 'o')
            plt.show()


main()
