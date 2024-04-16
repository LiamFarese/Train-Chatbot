
# imports #

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
from pandas.core.interchange import dataframe

from sklearn.neighbors import KNeighborsRegressor


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
def extract_day_from_rid(rid_string):

    return int(rid_string[6:8])


def get_full_historical_dataset(print_progress=False):

    data = pd.DataFrame(columns=['month', 'day', 'day_of_week', 'duration', 'delay'])

    for year in range(2017, 2023):

        print(f"Processing year: {year}...")

        for month in range(1, 13):

            if print_progress:

                print(f"\tProcessing month: {month}...")


            historical = get_historical_data(year, month)

            # filtered out where needed columns are not empty
            hist_filtered = (

                historical.loc)[

                    (historical['pta'].notnull())
                    & (historical['ptd'].notnull())
                    & (historical['arr_at'].notnull())
                    & (historical['rid'].notnull())
                ]

            previous_row = None

            for index, row in hist_filtered.iterrows():

                if previous_row is None:

                    previous_row = row
                    continue


                # extract times to values
                arr_at = extract_time_to_seconds(row['arr_at'])
                pta = extract_time_to_seconds(row['pta'])

                # if the format is incorrect, one of these will be None
                if arr_at is None or pta is None:

                    continue


                # planned duration = departure of previous vs arrival of current
                duration = pta - extract_time_to_seconds(previous_row['ptd'])

                # if the duration is below 0, do not put in the graph
                if duration <= 0:

                    continue


                # extract delay, if negative just set to 0
                delay = max(arr_at - pta, 0)
                day = extract_day_from_rid(str(row['rid']))

                # get the remainder of day / 7 and add 1 to get the day of the week
                day_of_the_week = day % 7 + 1

                # if the delay is over 0, there has been delay
                new_row = {'month':         month,
                           'day_of_week':   day_of_the_week,
                           'day':           day,
                           'duration':      duration,
                           'delay':         delay}

                data = data._append(new_row, ignore_index=True)

                previous_row = row


    return data


# main #

def main():

    data = None
    option = 1

    while option > 0:

        option = int(input(
            "Select an option:\n"
            "0. Exit\n"
            "[1]. Full\n"
            "2. Extract table\n"
            "3. Train model\n"
            "9. Extract Graph\n"
            "Your Answer: "))

        if option == 1 or option == 2:

            data = get_full_historical_dataset(True)
            data.to_csv(historical_table_path)
            print("table saved!\n")


        # all options after 2 require the table to be loaded
        if option == 1 or option > 2:

            if data is None:

                data = pd.read_csv(historical_table_path)


        if option == 1 or option == 9:

            print(len(data.loc[data['duration'] <= 120]))

            plt.plot(data['duration'], data['delay'], 'o')
            plt.show()


main()
