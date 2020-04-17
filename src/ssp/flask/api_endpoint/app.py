#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

#https://www.javacodemonk.com/named-entity-recognition-spacy-flask-api-1678a5df
import gin
from flask import Flask, render_template, request, url_for, request, abort, jsonify
import spacy

from ssp.utils.config_manager import ConfigManager
# from ssp.dl.classifier.naive_text_classifier import NaiveTextClassifier

nlp = spacy.load('en_core_web_sm')

# text_classifier = NaiveTextClassifier(hdfs_host="localhost", hdfs_port=9000, model_dir=f"{os.path.expanduser('~')}/ssp/model/raw_tweet_dataset_0/")

app = Flask(__name__)

@app.route('/')
def index():
    """
    Home page with list of links for upload and download
    :return:
    """
    return render_template('layouts/index.html')


@app.route('/text/ner/spacy', methods=["POST"])
def get_ner():
    res = {}
    if not request.json or not "text" in request.json:
        abort(400)
    print(request.json)
    text = request.json["text"]
    doc = nlp(text)
    for ent in doc.ents:
        res[ent.label_] = ent.text
    return jsonify({"res": str(res)}), 201

#https://towardsdatascience.com/deploying-keras-models-using-tensorflow-serving-and-flask-508ba00f1037
@app.route('/text/classification/naive/', methods=["POST"])
def text_clasification():
    res = {}
    if not request.json or not "text" in request.json:
        abort(400)
    text = request.json["text"]
    res=text
    # res = text_classifier.predict(text)
    return jsonify({"res": str(res)}), 201


@gin.configurable
def api_endpoint(host,
                 port):
    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    gin.parse_config_file(config_file="config/api_endpoint.gin")
    api_endpoint()
