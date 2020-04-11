# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, url_for, jsonify
import pandas as pd
import json
import plotly
import gin

app = Flask(__name__)
app.debug = True


@gin.configurable
class PostgresqlInfo():

    def __init__(self,
                 host="localhost",
                 database="sparkstreamingdb",
                 user="sparkstreaming",
                 password="sparkstreaming",
                 port=5432):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port


@app.route('/')
def index():
    """
    Home page with list of links for upload and download
    :return:
    """
    return render_template('layouts/index.html')

@app.route('/ai_tweets')
def ai_tweets():
    """
    Home page with list of links for upload and download
    :return:
    """
    return render_template('layouts/ai_tweets.html')



@gin.configurable
def ai_tweets_dashboard(host,
                        port):
    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    gin.parse_config_file(config_file="config/ai_tweets_dashboard.gin")
    ai_tweets_dashboard()