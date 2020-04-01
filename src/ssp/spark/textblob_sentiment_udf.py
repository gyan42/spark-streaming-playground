from textblob import TextBlob
from pyspark.sql.functions import udf


def analyze_sentiment(text):
    testimonial = TextBlob(text)
    sent = testimonial.sentiment.polarity
    neutral_threshold = 0.05
    if sent >= neutral_threshold:       # positive
        return 1
    elif sent > -neutral_threshold:     # neutral
        return 0
    else:                               # is_ml_tweet
        return -1

textblob_sentiment_analysis_udf = udf(analyze_sentiment)


