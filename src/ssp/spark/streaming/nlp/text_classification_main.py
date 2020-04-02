import argparse
import gin

from ssp.spark.streaming.nlp.text_classification import SreamingTextClassifier

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor NLP pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    nlp_processing = SreamingTextClassifier()

    gin.parse_config_file(parsed_args.config_file)

    nlp_processing.process()
