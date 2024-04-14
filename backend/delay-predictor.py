
# imports #

import numpy as np
import matplotlib.pyplot as plt

import pandas as pd
from pandas.core.interchange import dataframe

from sklearn.neighbors import KNeighborsRegressor


# constants #

historical_data_path = 'historical-data'


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


def get_full_historical_dataset():

    #data = get_historical_data(2022, 1)

    # data.loc[
    #     (data['pta'].notnull())
    #     & (data['arr_at'].notnull())
    #     & (len(data['pta']) < 10),
    #     ['pta', 'arr_at']]

    data = pd.DataFrame(columns=['month', 'delay'])

    historical = get_historical_data(2022, 1)

    hist_filtered = (

        historical.loc)[

            (historical['pta'].notnull())
            & (historical['arr_at'].notnull())
        ]


    for index, row in hist_filtered.iterrows():

        # check time can be extracted
        if len(row['pta']) != 5 or len(row['arr_at']) != 5:

            break

        # extract delay
        delay = (

            # extract hours from pta
            (int(row['arr_at'][0:2]) * 3600
                # extract minutes from pta
                + int(row['arr_at'][3:5]) * 60)
            -
            # extract hours from arr_at
            (int(row['pta'][0:2]) * 3600
                # extract minutes from arr_at
                + int(row['pta'][3:5]) * 60)
        )

        # if the delay is over 0, there has been delay
        new_row = {'month': index, 'delay': delay > 0}

        data = data._append(new_row, ignore_index=True)


    return data


# main #

def main():

    model = KNeighborsRegressor(n_neighbors=5)

    data = get_full_historical_dataset()

    print(data)
    print(data.loc[data['delay']])


main()
