#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import gin
from flask import Flask, render_template
import json
from flask import jsonify
import plotly
from ssp.posgress.dataset_base import PostgresqlConnection
from ssp.utils.config_manager import ConfigManager
from ssp.utils.postgresql import postgressql_connection, create_pandas_table

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('layouts/index.html')

@app.route('/trending_tags')
def trending_tags():
    db = PostgresqlConnection()

    try:
        df = db.query_to_df("select * from trending_hashtags")

        df = df.sort_values(["count"], ascending=0)
        df = df[df["hashtag"] != "no tags"]
        df = df.iloc[:20]

        data = [
            #go.Bar(x=df["hashtag"], y=df["count"], name='TrendingTags')
            dict(
                data=[
                    dict(
                        x=df["hashtag"],
                        y=df["count"],
                        type='bar'
                    ),
                ]
            )
        ]

        graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

        ids = ["Trending Tweets"]
        conn.close()
        return render_template('layouts/graph_display.html',
                               ids=ids,
                               graphJSON=graphJSON)
    except Exception as e:
        return jsonify("{Table `trending_hashtags` is not yet created}")


@gin.configurable
def trending_hashtags(host,
                      port):
    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    gin.parse_config_file(config_file="config/trending_hashtags.gin")
    trending_hashtags()