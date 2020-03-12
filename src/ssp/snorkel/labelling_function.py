from snorkel.labeling import labeling_function
from snorkel.labeling import LabelModel, PandasLFApplier

import re
# Set voting values.
# all other tweets
ABSTAIN = -1
# tweets that talks about science, nature, wild life, conspiracy, space, occult, astrology, horoscope
POSITIVE = 0
# tweets taht talks about politics, sad, vulgar etc.,
NEGATIVE = 1

# Understanding a bit of precision and recall is very important for the classification
# https://towardsdatascience.com/precision-vs-recall-386cf9f89488
# https://medium.com/@mlengineer/generative-and-discriminative-models-af5637a66a3

TRAIN_DATASET = None # 200 records unlabled dataset
TEST_DATASET = None # 200 records labeled set
VAL_DATASET = None # 200 records
LF_DATASET = None # 200 records


@labeling_function()
def postive(tweet_text):
    TAGS = r"(science|nature|wild life|conspiracy|space|occult|astrology|horoscope)"
    return POSITIVE if re.search(TAGS, tweet_text.lower()) else ABSTAIN

@labeling_function()
def negative(tweet_text):
    TAGS = r"(sad|bad|fuck|shit|)"
    return POSITIVE if re.search(TAGS, tweet_text.lower()) else ABSTAIN

lfs = [postive, negative]