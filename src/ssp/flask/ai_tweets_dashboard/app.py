# -*- coding: utf-8 -*-
import re
from flask import Flask, render_template, request, url_for, jsonify
import pandas as pd
import json
import plotly
import gin
from flask_paginate import Pagination, get_page_args

from ssp.logger.pretty_print import print_error
from ssp.posgress.dataset_base import PostgresqlDatasetBase

app = Flask(__name__)
app.debug = True

PER_PAGE = 50


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


def repl_func(matchObj):
    href_tag, url = matchObj.groups()
    if href_tag:
        # Since it has an href tag, this isn't what we want to change,
        # so return the whole match.
        return matchObj.group(0)
    else:
        return '<a href="%s" target="_blank" >%s</a>' % (url, url)


pattern = re.compile(
    r'((?:<a href[^>]+>)|(?:<a href="))?'
    r'((?:https?):(?:(?://)|(?:\\\\))+'
    r"(?:[\w\d:#@%/;$()~_?\+\-=\\\.&](?:#!)?)*)",
    flags=re.IGNORECASE)


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
    db = PostgresqlDatasetBase()
    df = db.execute("select count(*) as count from ai_tweets")
    total = df["count"].values[0]
    print(df)
    print(total)

    page, _, _ = get_page_args(page_parameter='page',
                               per_page_parameter='per_page')
    # No updates and hence to scrolling
    # scroll_id = None
    per_page = PER_PAGE #per_page #TODO better way
    offset = per_page * (page-1)
    print_error([page, per_page, offset])

    data_df = db.execute(f"select * from ai_tweets limit {PER_PAGE} offset {offset}")

    # Pagination, listing only a subset at a time
    pagination = Pagination(page=page,
                            per_page=per_page,
                            total=total,
                            css_framework='bootstrap4')

    # print_error(data_df["id"].to_list())

    return render_template('layouts/ai_tweets.html',
                           len=data_df.shape[0],
                           prob=data_df["ai_prob"].to_list(),
                           text=[re.sub(pattern, repl_func, t) for t in data_df["text"].to_list()],
                           page=page,
                           per_page=per_page,
                           offset=offset,
                           pagination=pagination)



@gin.configurable
def ai_tweets_dashboard(host,
                        port):
    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    gin.parse_config_file(config_file="config/ai_tweets_dashboard.gin")
    ai_tweets_dashboard()