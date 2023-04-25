
# from utility_functions.py in solar stats
###############

import math
import sys
sys.path.append('pecos')
import pecos
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
import numpy as np

class Filterer:
    def __init__(self, df):
        self._df = df

    def out_of_bounds(self, col: str, min, max=None) -> pd.DataFrame:
            """
            Cleans out data that is not within bounds
            Args:
                col (str): The data column to clean
                min (Any): The minimum value for cleaning
                max (Any, optional): The maximum value for cleaning, should be the same type as min
            Returns:
                :obj:`pd.DataFrame`: The DataFrame with data removed based on filter
            """
            df = self._df.copy()
            if max:
                mask = df[col].between(min, max)
                return mask
            else:
                mask = df[col].gt(min)
                return mask


    def interval_change(
            self,
            col: str,
            interval: int,
            bound,
            direction = "positive",
        ) -> pd.DataFrame:
            """
            Calculates whether data is stagnant and/or abruptly changes using the difference between the max and min values within a rolling window.
            See: https://pecos.readthedocs.io/en/latest/apidoc/pecos.monitoring.html#pecos.monitoring.PerformanceMonitoring.check_delta
            Args:
                col (str): The data column to check
                interval (int): Interval in seconds
                bound (:obj:`list`): [lower bound, upper bound], None can be used in place of a lower or upper bound
                direction (str, optional):
                    Options = 'positive', 'negative', or None
                    If direction is positive, then only identify positive deltas (the min occurs before the max)
                    If direction is negative, then only identify negative deltas (the max occurs before the min)
                    If direction is None, then identify both positive and negative deltas
            Returns:
                :obj:`pd.DataFrame`: The DataFrame with columns not meeting the criteria filtered out
            """
            df = self._df.copy()
            # for some reason, key doesnt seem to limit the data in function, so extra column
            data = pd.DataFrame(df[col])
            mask = pecos.monitoring.check_delta(data, bound, interval, direction=direction)["mask"][col]
            return df.loc[mask], mask



    def completeness_score(self, frequency: str) -> pd.Series:
            """
            Calculates a completeness score for each day in the data.
            The completeness score for a given day is the fraction of time in the day for which there is data (a value other than NaN). The time duration attributed to each value is equal to the timestamp spacing of frequency.
            The completeness score for each day is the average completeness score of each column for each day.
            For example, a 24-hour time series with 30 minute timestamp spacing and 24 non-NaN values would have data for a total of 12 hours and therefore a completeness score of 0.5.
            Args:
                frequency (str): Frequency string for data (see pandas docs for types), if the data doesn't have a set frequency use the closet one for more accurate results, could be 1min, 5s, 1h etc
            Returns:
                :obj:`pd.Series`: The series containing the completeness score for each day
            """
            def _freq_to_seconds():
                delta = pd.to_timedelta(frequencies.to_offset(frequency))
                return delta.days * (1440 * 60) + delta.seconds
            freq_seconds = _freq_to_seconds()
            # calculates for each column, then averages each day together, then the entire dataset into one final score
            score = None
            for column in self._df.columns:
                daily_counts = self._df[column].resample("D").count()
                daily_completeness = (daily_counts * freq_seconds) / (1440 * 60)
                if score is None:
                    score = daily_completeness
                else:
                    score += daily_completeness
            score /= len(self._df.columns)
            return score.reindex(self._df.index, method="pad")
        
    
# Utility function for seasonality component 
def toYearFraction(date):
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch
    
    if isinstance(date, np.datetime64):
        ts = (date - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        date = datetime.utcfromtimestamp(ts)

    year = date.year
    
    startOfThisYear = datetime(year=year, month=1, day=1)
    startOfNextYear = datetime(year=year+1, month=1, day=1)
    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    return yearElapsed/yearDuration

def linear_lambda(st,ed):
    return lambda t: max( (t > st) * (t < ed) * (
                (t > st) * (t < ed) * (t - st) + (t >= ed) * (ed - st)) / 1000.0
                )

def square_lambda(st,ed):
    return lambda t: sum((t > st) * (t <= ed))

def seasonality(st,ed):
    toYearFraction()

def lambda_applier(stSeries, edSeries, transformer='square'):
    if transformer == 'square':
        return square_lambda(stSeries, edSeries)
    elif transformer == 'linear':
        return linear_lambda(stSeries, edSeries)
    
###################3