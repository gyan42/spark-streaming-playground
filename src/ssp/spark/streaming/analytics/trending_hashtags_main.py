import argparse
import gin

# http://docs.tweepy.org/en/latest/streaming_how_to.html
# we create this class that inherits from the StreamListener in tweepy StreamListener

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/default_ssp_config.gin",
                          required=False,
                          help="File path of gin config file")

    optparse.add_argument("-sw", "--mode",
                          type=str,
                          default="ai",
                          required=False,
                          help="Filter twitter stream including one of [ai|stopwords|ai_stopwords] keywords")

    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)
    from ssp.spark.streaming.analytics.trending_hashtags import TrendingHashTags
    nlp_processing = TrendingHashTags()
    nlp_processing.process()
