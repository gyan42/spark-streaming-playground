from pyspark.sql.functions import udf
import requests
import ast
from pyspark.sql.types import *


# Interesting use case : What if the end point gone for toss and
# Streaming has to recomputed for failed cases ?
from ssp.logger.pretty_print import print_info
from ssp.logger.pretty_print import print_error


def get_ner(text, url):

    data = {'text': text}
    tags = []
    try:
        r = requests.post(url=url, json=data)
        r.raise_for_status()
        data = r.json()["res"]
        data = eval(data)
        for key, value in zip(data.keys(), data.values()):
            tags.append((str(key), str(value)))
    except requests.exceptions.HTTPError as err:
        print(err)
        tags = ["URL_ERROR"]
    return tags

schema = ArrayType(StructType([
    StructField("ner", StringType(), False),
    StructField("word", StringType(), False)
]))


# TODO fixed for now, expose/configure the URL through gin config
def get_ner_udf(is_docker):
    if is_docker:
        url = "http://host.docker.internal:30123/text/ner/spacy"
        return udf(lambda x: get_ner(text=x, url=url), schema)
    else:
        url = "http://127.0.0.1:30123/text/ner/spacy"
        return udf(lambda x: get_ner(text=x, url=url), schema)


if __name__ == "__main__":

    try:
        URL = "http://host.docker.internal:30123/text/ner/spacy"
        print_info(f"Trying URL : {URL} ")
        # sending get request and saving the response as response object
        data = get_ner(text="Wow! this is Wednesday night now and here the lazy Mageswaran coding me", url=URL)
        print(data)
    except:
        print_error("Failed!")
        URL = "http://127.0.0.1:30123/text/ner/spacy"
        print_info(f"Trying URL : {URL} ")
        # sending get request and saving the response as response object
        data = get_ner(text="Wow! this is Wednesday night now and here the lazy Mageswaran coding me", url=URL)
        print(data)
