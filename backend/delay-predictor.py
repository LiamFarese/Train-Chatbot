
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


def get_full_historical_dataset(print_progress=False):

    data = pd.DataFrame(columns=['month', 'delay'])

    for month in range(1, 13):

        if print_progress:

            print(f"Processing month: {month}...")


        historical = get_historical_data(2022, month)

        # filtered out where needed columns are not empty
        hist_filtered = (

            historical.loc)[

                (historical['pta'].notnull())
                & (historical['arr_at'].notnull())
            ]

        previous_row = None

        for index, row in hist_filtered.iterrows():

            if previous_row is None:

                previous_row = row
                pass


            # extract times to values
            arr_at = extract_time_to_seconds(row['arr_at'])
            pta = extract_time_to_seconds(row['pta'])

            # if the format is incorrect, one of these will be None
            if arr_at is None or pta is None:

                pass


            # extract delay, if negative just set to 0
            delay = max(arr_at - pta, 0)

            # if the delay is over 0, there has been delay
            new_row = {'month': month, 'delay': delay}

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
            "Your Answer: "))

        if option == 1 or option == 2:

            data = get_full_historical_dataset(True)
            data.to_csv(historical_table_path)
            print("table saved!\n")


        if option == 1 or option == 3:

            if data is None:

                data = pd.read_csv(historical_table_path)


            plot = data.plot()
            fig = plot.get_figure()
            fig.savefig("historical_data_plot.png")


main()
