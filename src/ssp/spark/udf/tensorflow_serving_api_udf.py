import requests
import json
from pyspark.sql.types import FloatType, ArrayType
from pyspark.sql.functions import udf

from ssp.logger.pretty_print import print_error, print_warn
from ssp.dl.tf.classifier import NaiveTextClassifier
from ssp.logger.pretty_print import print_info


def predict_text_class(text, url, tokenizer_path):
    classifer = NaiveTextClassifier()
    # TODO is this right way to load the tokenizer? Move this to a flask API as one extra layer
    classifer.load_tokenizer(tokenizer_path=tokenizer_path)
    text = list(classifer.transform([text])[0])
    text = [int(t) for t in text]
    data = json.dumps({"signature_name": "serving_default", "instances": [text]})
    headers = {"content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    return float(predictions[0][1])


schema = FloatType()


def get_text_classifier_udf(is_docker, tokenizer_path):
    if is_docker: #when the example is trigger inside the Docker environment
        url = "http://host.docker.internal:30125/v1/models/naive_text_clf:predict"
        return udf(lambda x: predict_text_class(text=x, tokenizer_path=tokenizer_path, url=url), schema)
    else:
        url = "http://localhost:8501/v1/models/naive_text_clf:predict"
        return udf(lambda x: predict_text_class(text=x, tokenizer_path=tokenizer_path, url=url), schema)

def predict(text):
    print("\n")
    print_info(f"Text : {text} ")
    try:
        URL = "http://host.docker.internal:30125/v1/models/naive_text_clf:predict"
        data = predict_text_class(text=text,
                                  url=URL,
                                  tokenizer_path="~/ssp/model/raw_tweet_dataset_0/naive_text_classifier/1/")
        print_warn(URL)
        print(data)
        exit(0)
    except:
        pass

    try:
        URL = "http://localhost:8501/v1/models/naive_text_clf:predict"
        data = predict_text_class(
            text=text,
            url=URL,
            tokenizer_path="~/ssp/model/raw_tweet_dataset_0/naive_text_classifier/1/")
        print_warn(URL)
        print(data)
        exit(0)
    except:
        pass

    try:
        URL = "http://127.0.0.1:30125/v1/models/naive_text_clf:predict"
        data = predict_text_class(
            text=text,
            url=URL,
            tokenizer_path="~/ssp/model/raw_tweet_dataset_0/naive_text_classifier/1/")
        print_warn(URL)
        print(data)
        exit(0)
    except:
        pass


if __name__ == "__main__":
    predict("📰Machine learning as a tool to explore cognitive profiles of epileptic patients. Neuropsychological data science are meaningful artificial intelligence 📈🔍| Home https://t.co/cAQ2vZYxk2")
    predict("This is a random text to check whats the prediction...home so it gets classified as 0")

# export PYTHONPATH=$(pwd)/src/:$PYTHONPATH