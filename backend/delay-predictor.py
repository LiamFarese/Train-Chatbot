
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
def extract_time_from_string(time_string):

    return dt.datetime.strptime(time_string, '%H:%M')


def extract_seconds_from_string(time_string):

    time = extract_time_from_string(time_string)

    total_seconds = 0

    total_seconds += time.hour * 3600
    total_seconds += time.minute * 60


    return total_seconds


# extracts the day from the historical data
def extract_date_from_rid(rid_string):

    #year = int(rid_string[0:4])
    #month = int(rid_string[4:6])
    #day = int(rid_string[6:8])

    return dt.datetime.strptime(rid_string[:8], '%Y%m%d')


# extract and save the full dataset from the historical data
# into a table with columns month, day, day_of_week, duration, delay
def get_full_historical_dataset(print_progress=False):

    data = {

        'delay': [],
        'departure_delay': [],
        'day_of_week': [],
        'day_of_month': [],
        'weekday': [],
        'on_peak': [],
        'hour': [],
    }

    for year in range(2017, 2023):

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
                    & (historical['ptd'].notnull())
                    & (historical['dep_at'].notnull())
                ]

            previous_row = None
            previous_day_of_month = None

            for index, row in hist_filtered.iterrows():

                if previous_row is None:

                    previous_row = row
                    continue


                # get delay
                a_predicted = extract_seconds_from_string(row['pta'])
                a_actual = extract_seconds_from_string(row['arr_at'])
                delay = a_predicted - a_actual

                # get delay and departure delay
                d_predicted = extract_seconds_from_string(previous_row['ptd'])
                d_actual = extract_seconds_from_string(previous_row['dep_at'])
                departure_delay = d_predicted - d_actual

                # get day of week and month and if weekday
                date = extract_date_from_rid(str(row['rid']))
                day_of_month = date.day

                if previous_day_of_month != day_of_month:

                    previous_day_of_month = day_of_month
                    continue


                day_of_week = date.weekday()
                weekday = day_of_week == 5 or 6

                # get hour and if on peak
                time = extract_time_from_string(str(row['pta']))
                on_peak = time.hour >= 9


                data['delay']           .append(delay)
                data['departure_delay'] .append(departure_delay)

                data['day_of_week']     .append(day_of_week)
                data['day_of_month']    .append(day_of_month)
                data['weekday']         .append(int(weekday))

                data['on_peak']         .append(int(on_peak))
                data['hour']            .append(time.hour)


    return pd.DataFrame.from_dict(data)


def train_model(data, model):

    d = data.loc[data['delay'] < 20000]

    X = d[data.columns.drop('delay')]
    y = d['delay']

    print(X)

    seed = 91
    test_size = 0.2

    X_train, X_test, y_train, y_test = train_test_split(
       X, y, test_size=test_size, random_state=seed)

    model.fit(X_train, y_train)
    y_predict = model.predict(X_test)

    print(model.score(X_test, y_test))

    plt.scatter(X_train['day_of_month'], y_train, color='black', label='training data')
    plt.plot(X_test['day_of_month'], y_predict, color='b', label='Linear Regression')
    plt.show()


# main #

def main():

    t = dt.datetime.strptime('00:12:02', '%H:%M:%S')
    print(t)

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

            model = KNeighborsRegressor()

            train_model(data, model)


        if option == 1 or option == 9:

            averages = []

            for i in range(0, 24):

                r = data.loc[
                    (data['hour'] == i)]['delay']

                averages.append(r.mean())


            plt.plot(range(0, 24), averages, 'o')
            plt.show()


main()
