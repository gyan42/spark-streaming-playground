#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

# https://stackoverflow.com/questions/18603270/progress-indicator-during-pandas-operations

import pandas as pd
import numpy as np
import multiprocessing
from functools import partial


def _df_split(tup_arg, **kwargs):
    split_ind, df_split, df_f_name = tup_arg
    return (split_ind, getattr(df_split, df_f_name)(**kwargs))


def df_multi_core(df, df_f_name, subset=None, njobs=-1, **kwargs):
    if njobs == -1:
        njobs = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=njobs)

    try:
        splits = np.array_split(df[subset], njobs)
    except ValueError:
        splits = np.array_split(df, njobs)

    pool_data = [(split_ind, df_split, df_f_name) for split_ind, df_split in enumerate(splits)]
    results = pool.map(partial(_df_split, **kwargs), pool_data)
    pool.close()
    pool.join()
    results = sorted(results, key=lambda x:x[0])
    results = pd.concat([split[1] for split in results])
    return results