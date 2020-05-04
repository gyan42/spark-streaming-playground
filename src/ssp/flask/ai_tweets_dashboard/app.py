#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import re
from flask import Flask, render_template
import gin
from flask_paginate import Pagination, get_page_args

from ssp.logger.pretty_print import print_error
from ssp.posgress.dataset_base import PostgresqlConnection

app = Flask(__name__)
app.debug = True

PER_PAGE = 50


def repl_func(matchObj):
    """
    Adds the HTML anchor to URLs
    :param matchObj:
    :return:
    """
    href_tag, url = matchObj.groups()
    if href_tag:
        # Since it has an href tag, this isn't what we want to change,
        # so return the whole match.
        return matchObj.group(0)
    else:
        return '<a href="%s" target="_blank" >%s</a>' % (url, url)

# pattern to identify the URLs
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

@app.route('/all_tweets')
def all_tweets():
    """
    Home page with list of links for upload and download
    :return:
    """
    db = PostgresqlConnection()
    df = db.query_to_df("select count(*) as count from ai_tweets")
    total = df["count"].values[0]
    # print(df)
    # print(total)

    page, _, _ = get_page_args(page_parameter='page',
                               per_page_parameter='per_page')
    # No updates and hence to scrolling
    offset = PER_PAGE * (page-1)
    print_error([page, PER_PAGE, offset])

    data_df = db.query_to_df(f"select * from ai_tweets limit {PER_PAGE} offset {offset}")

    # Pagination, listing only a subset at a time
    pagination = Pagination(page=page,
                            per_page=PER_PAGE,
                            total=total,
                            css_framework='bootstrap4')

    return render_template('layouts/all_tweets.html',
                           len=data_df.shape[0],
                           prob=data_df["ai_prob"].to_list(),
                           text=[re.sub(pattern, repl_func, t) for t in data_df["text"].to_list()],
                           page=page,
                           per_page=PER_PAGE,
                           offset=offset,
                           pagination=pagination)


@app.route('/ai_tweets')
def ai_tweets():
    """
    Home page with list of links for upload and download
    :return:
    """
    db = PostgresqlConnection()
    df = db.query_to_df("select count(*) as count from ai_tweets where ai_prob > 0.5")
    total = df["count"].values[0]
    # print(df)
    # print(total)

    page, _, _ = get_page_args(page_parameter='page',
                               per_page_parameter='per_page')
    # No updates and hence to scrolling
    offset = PER_PAGE * (page-1)
    print_error([page, PER_PAGE, offset])

    data_df = db.query_to_df(f"select * from ai_tweets where ai_prob > 0.5 limit {PER_PAGE} offset {offset}")

    # Pagination, listing only a subset at a time
    pagination = Pagination(page=page,
                            per_page=PER_PAGE,
                            total=total,
                            css_framework='bootstrap4')

    return render_template('layouts/ai_tweets.html',
                           len=data_df.shape[0],
                           prob=data_df["ai_prob"].to_list(),
                           text=[re.sub(pattern, repl_func, t) for t in data_df["text"].to_list()],
                           page=page,
                           per_page=PER_PAGE,
                           offset=offset,
                           pagination=pagination)


@gin.configurable
def ai_tweets_dashboard(host,
                        port):
    app.run(debug=True, host=host, port=port)


if __name__ == '__main__':
    gin.parse_config_file(config_file="config/ai_tweets_dashboard.gin")
    ai_tweets_dashboard()