from pyspark.sql.functions import udf
import requests
import ast
from pyspark.sql.types import *


# Interesting use case : What if the end point gone for toss and
# Streaming has to recomputed for failed cases ?
from ssp.utils.pretty_print import print_error


def get_ner(text, url="http://host.docker.internal:30123/spacy/api/v0.1/ner"):
    data = {'text': text}
    tags = []
    try:
        r = requests.post(url=url, json=data)
        r.raise_for_status()
        data = r.json()["res"]
        data = eval(data)
        for key, value in zip(data.keys(), data.values()):
        # print_error(tags)
            tags.append((str(key), str(value)))
    except requests.exceptions.HTTPError as err:
        print(err)
        tags = ["URL_ERROR"]
    return tags

schema = ArrayType(StructType([
    StructField("ner", StringType(), False),
    StructField("word", StringType(), False)
]))
get_ner_udf = udf(get_ner, schema)


if __name__ == "__main__":

    URL = "http://host.docker.internal:30123/spacy/api/v0.1/ner"

    # sending get request and saving the response as response object
    data = get_ner(text="Wow! this is Wednesday night now and here the lazy Mageswaran coding me")

    print(data)
