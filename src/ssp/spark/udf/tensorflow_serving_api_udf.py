import requests
import json
from pyspark.sql.types import StructType, StringType, FloatType
from pyspark.sql.functions import udf

from ssp.logger.pretty_print import print_error
from ssp.dl.classifier import NaiveTextClassifier
from ssp.logger.pretty_print import print_info


def predict_text_class(text, url, tokenizer_path):
    classifer = NaiveTextClassifier()
    classifer.load_tokenizer(tokenizer_path=tokenizer_path)
    text = list(classifer.transform([text])[0])
    text = [int(t) for t in text]
    data = json.dumps({"signature_name": "serving_default", "instances": [text]})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    return float(predictions[0][0])


schema = FloatType()


def get_text_classifier_udf(is_docker, tokenizer_path):
    if is_docker:
        pass
        # url = "http://host.docker.internal:30123/text/ner/spacy"
        # return udf(lambda x: get_ner(text=x, url=url), schema)
    else:
        url = "http://localhost:8501/v1/models/naive_text_clf:predict"
        return udf(lambda x: predict_text_class(text=x, tokenizer_path=tokenizer_path, url=url), schema)


if __name__ == "__main__":
    try:
        URL = "http://host.docker.internal:30123/text/ner/spacy"
        print_info(f"Trying URL : {URL} ")
        # sending get request and saving the response as response object
        data = predict_text_class(text="Wow! this is Wednesday night now and here the lazy Mageswaran coding me",
                                  url=URL,
                                  tokenizer_path="~/ssp/model/raw_tweet_dataset_0/naive_text_classifier/1/")
        print(data)
    except:
        print_error("Failed!")
        URL = "http://localhost:8501/v1/models/naive_text_clf:predict"
        print_info(f"Trying URL : {URL} ")
        # sending get request and saving the response as response object
        data = predict_text_class(text="Wow! this is Wednesday night now and here the lazy Mageswaran coding me",
                                  url=URL,
                                  tokenizer_path="~/ssp/model/raw_tweet_dataset_0/naive_text_classifier/1/")
        print(data)

# export PYTHONPATH=$(pwd)/src/:$PYTHONPATH