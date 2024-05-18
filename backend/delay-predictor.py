
# imports #

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

import pickle

from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression, BayesianRidge
from sklearn.ensemble import AdaBoostRegressor, RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split

import datetime as dt

import pickle


# constants #

historical_data_path = 'historical-data'
historical_table_path = f'{historical_data_path}/historical_table.csv'
station_dict_path = f'{historical_data_path}/station_dict.pkl'
seed = 91


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

    return dt.datetime.strptime(rid_string[:8], '%Y%m%d')


# extract and save the full dataset from the historical data
# into a table with columns month, day, day_of_week, duration, delay
def get_full_historical_dataset(print_progress=False):

    data = {

        'delay': [],
        'departure_delay': [],
        'day_of_week': [],
        'day_of_year': [],
        'weekday': [],
        'on_peak': [],
        'hour': [],
        'first_stop': [],
        'second_stop': [],
    }

    station_dict = {}

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
                    & (historical['tpl'].notnull())
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

                # if something's gone wrong with the times, skip
                if delay > 10000 or delay < -10000:

                    continue


                # get delay and departure delay
                d_predicted = extract_seconds_from_string(previous_row['ptd'])
                d_actual = extract_seconds_from_string(previous_row['dep_at'])
                departure_delay = d_predicted - d_actual

                # get day of week and month and if weekday
                date = extract_date_from_rid(str(row['rid']))
                day_of_month = date.day

                if previous_day_of_month != day_of_month:

                    previous_day_of_month = day_of_month
                    previous_row = row
                    continue


                day_of_week = date.weekday()
                weekday = day_of_week == 5 or 6

                day_of_year = date.timetuple().tm_yday

                # get hour and if on peak
                time = extract_time_from_string(str(row['pta']))
                on_peak = time.hour >= 9

                # get first and second stop
                first_stop = previous_row['tpl']

                if first_stop not in station_dict:

                    # index station as next possible + 1
                    station_dict[first_stop] = len(station_dict) + 1


                # get first and second stop
                second_stop = row['tpl']

                if second_stop not in station_dict:
                    # index station as next possible + 1
                    station_dict[second_stop] = len(station_dict) + 1


                data['delay']           .append(delay)
                data['departure_delay'] .append(departure_delay)

                data['day_of_week']     .append(day_of_week)
                data['day_of_year']     .append(day_of_year)
                data['weekday']         .append(int(weekday))

                data['on_peak']         .append(int(on_peak))
                data['hour']            .append(time.hour)

                data['first_stop']     .append(station_dict[first_stop])
                data['second_stop']     .append(station_dict[second_stop])

                previous_row = row


    with open(station_dict_path, 'wb') as file:
        pickle.dump(station_dict, file)

    return pd.DataFrame.from_dict(data)


def train_model(data, model):

    X = data[data.columns.drop('delay')]
    y = data['delay']

    test_size = 0.2

    X_train, X_test, y_train, y_test = train_test_split(
       X, y, test_size=test_size, random_state=seed)

    model.fit(X_train, y_train)
    y_predict = model.predict(X_test)

    return model.score(X_test, y_test)


# main #

def main():

    data = None
    station_dict = None
    option = 1

    while option > 0:

        option = int(input(
            "Select an option:\n"
            "0. Exit\n"
            "1. Full\n"
            "2. Extract table\n"
            "3. Train model\n"
            "4. Save model\n"
            "9. Extract Graph\n"
            "Your Answer: "))


        full = option == 1


        if full or option == 2:

            data = get_full_historical_dataset(True)
            data.to_csv(historical_table_path)
            print("table saved!\n")


        # all options after 2 require the table and dict to be loaded
        if full or option > 2:

            if data is None:

                data = pd.read_csv(historical_table_path, index_col=0)


            if station_dict is None:

                with open(station_dict_path, 'rb') as file:
                    station_dict = pickle.load(file)

                print(station_dict)


        if full or option == 3:

            print('Testing Random Forest Regressor')

            model = RandomForestRegressor(max_depth=9, max_features=4)
            score = train_model(data, model)
            print(f'\tscore={score}')


            print('Testing Decision Tree Regressor')

            model = DecisionTreeRegressor()
            score = train_model(data, model)
            print(f'\tmax_depth=None, score={score}')

            for i in range(5, 15):

                model = DecisionTreeRegressor(max_depth=i)
                score = train_model(data, model)
                print(f'\tmax_depth={i}, score={score}')


            for i in range(1, 10):

                model = DecisionTreeRegressor(max_features=i)
                score = train_model(data, model)
                print(f'\tmax_features={i}, score={score}')


            print('Testing Ada Boost Regressor')

            estimator = DecisionTreeRegressor()
            model = AdaBoostRegressor(estimator=estimator, random_state=seed)
            score = train_model(data, model)
            print(f'\tmax_depth=None, max_features=None, score={score}')

            estimator = DecisionTreeRegressor(max_depth=9, max_features=4)
            model = AdaBoostRegressor(estimator=estimator, random_state=seed)
            score = train_model(data, model)
            print(f'\tmax_depth=9, max_features=4, score={score}')

            estimator = DecisionTreeRegressor(max_depth=9, max_features=None)
            model = AdaBoostRegressor(estimator=estimator, random_state=seed)
            score = train_model(data, model)
            print(f'\tmax_depth=9, max_features=None, score={score}')

            for i in range(3, 6):

                estimator = DecisionTreeRegressor(max_depth=None, max_features=i)
                model = AdaBoostRegressor(estimator=estimator, random_state=seed)
                score = train_model(data, model)
                print(f'\tmax_depth=None, max_features={i}, score={score}')


            print('Testing knn')

            for i in range(20, 30):

                model = KNeighborsRegressor(n_neighbors=i, n_jobs=-1)
                score = train_model(data, model)

                print(f'\tn_neighbours={i}, score={score}')


            print('Testing Linear')
            model = LinearRegression()
            score = train_model(data, model)
            print(f'\tScore={score}')


            print('Testing Bayesian')
            model = BayesianRidge()
            score = train_model(data, model)
            print(f'\tScore={score}')


        if full or option == 4:

            print("Saving...")

            model = RandomForestRegressor(max_depth=9, max_features=4)

            with open('model.pickle', 'wb') as file:
                pickle.dump(model, file)

            print("Saved!")

            with open('model.pickle', 'rb') as file:
                model_loaded = pickle.load(file)

            print("Loading worked!")



        if option == 9:

            averages = []

            for i in range(0, 24):

                r = data.loc[
                    (data['hour'] == i)]['delay']

                averages.append(r.mean())


            plt.plot(range(0, 24), averages, 'o')
            plt.show()


main()
