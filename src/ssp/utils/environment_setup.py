import os
import random
import numpy as np
import pandas as pd

DISPLAY_ALL_TEXT = False
pd.set_option("display.max_colwidth", 0 if DISPLAY_ALL_TEXT else 50)

# Turn off TensorFlow logging messages
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
# For reproducibility
os.environ["PYTHONHASHSEED"] = "0"

"""
Its important to set random seed to reproduce the results.
"""
random.seed(42)
np.random.seed(42)