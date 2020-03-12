import os
import shutil
import sys

from flask import Flask, render_template, request, url_for, jsonify
import pandas as pd
import json
import plotly
from werkzeug.datastructures import FileStorage

from ssp.utils.config_manager import ConfigManager
from ssp.utils.postgresql import postgressql_connection, create_pandas_table
from flask_paginate import Pagination, get_page_args

# https://gist.github.com/mozillazg/69fb40067ae6d80386e10e105e6803c9#file-index-html-L5
# https://github.com/doccano/doccano

app = Flask(__name__)
app.debug = True

STORE_PATH = os.path.expanduser("~") + "/text_tagger/"

def check_n_mk_dirs(path, is_remove=False):
    if os.path.exists(path):
        if is_remove:
            shutil.rmtree(path)
    else:
        os.makedirs(path)


@app.route('/')
def index():
    return render_template('layouts/index.html')


@app.route('/upload_data', methods=['GET', 'POST'])
def upload_data():
    """
    Upload the user file into 'STORE_PATH'/data/ after deleting any old files in the path.
    :return:
    """
    print("------")
    if request.method == 'POST':
        check_n_mk_dirs(path=STORE_PATH + "/data/", is_remove=True)
        check_n_mk_dirs(path=STORE_PATH + "/data/", is_remove=False)
        file: FileStorage = request.files.get('file')
        if "csv" in file.content_type:
            df = pd.read_csv(file)
            df.to_csv(STORE_PATH + "/data/" +file.filename)
        return render_template('layouts/upload_data.html', count=df.shape[0], file=str(file.filename))
    return render_template('layouts/upload_data.html', count=0, file="---")

@app.route('/upload_labels', methods=['GET', 'POST'])
def upload_labels():
    """
    Upload the user label file into 'STORE_PATH' after deleting any old files in the path.
    :return:
    """
    if request.method == 'POST':
        check_n_mk_dirs(path=STORE_PATH + "/labels/", is_remove=True)
        check_n_mk_dirs(path=STORE_PATH + "/labels/", is_remove=False)
        file: FileStorage = request.files.get('file')
        if "csv" in file.content_type:
            df = pd.read_csv(file)
            df.to_csv(STORE_PATH + "/labels/" + file.filename)
        return render_template('layouts/upload_label.html', count=df.shape[0], file=str(file.filename))
    return render_template('layouts/upload_label.html', count=0, file="---")

def get_subset(df, offset=0, per_page=10):
    return df.iloc[offset: offset + per_page]


@app.route('/tag_text', methods=['GET', 'POST'])
def tag_text():
    data_files = os.listdir(STORE_PATH + "/data/")
    label_files = os.listdir(STORE_PATH + "/labels/")
    if len(data_files) == 0 or len(label_files) == 0:
        data_file = "---"
        return jsonify("No File to process!")
    else:
        data_file = data_files[0]
        label_file = label_files[0]
        df = pd.read_csv(STORE_PATH + "/data/" + data_file)
        label_df = pd.read_csv(STORE_PATH + "/labels/" + label_file)
        label_df["index"] = label_df["index"].astype(int)
        STRING_2_INDEX = dict(zip(label_df["label"], label_df["index"]))
        INDEX_2_STRING = dict(zip(STRING_2_INDEX.values(), STRING_2_INDEX.keys()))
        total = df.shape[0]

        if request.method == 'POST':
            response = request.form.to_dict()
            print(response)
            page, per_page, offset = int(response["page"]), int(response["per_page"]), int(response["offset"])
            df.at[int(response["id"])-1, "label"] = STRING_2_INDEX[response["option"]]
            df.to_csv(STORE_PATH + "/data/" + data_file, index=False)
            scroll_id = response["id"]
        else:
            page, per_page, offset = get_page_args(page_parameter='page',
                                                   per_page_parameter='per_page')
            scroll_id = None

        df = get_subset(df=df, offset=offset, per_page=per_page)

        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total,
                                css_framework='bootstrap4')

        return render_template('layouts/tagger.html',
                               scroll_id=scroll_id,
                               page=page,
                               per_page=per_page,
                               offset=offset,
                               pagination=pagination,
                               file=data_file,
                               url=url_for("tag_text", variable=tag_text),
                               len=df.shape[0],
                               id=df["id"].to_list(),
                               text=df["text"].to_list(),
                               label=df["label"].to_list(),
                               label_string=[INDEX_2_STRING[int(i)] for i in df["label"].to_list()],
                               options=list(STRING_2_INDEX.keys()))


if __name__ == '__main__':
    config = ConfigManager(config_path="config.ini")
    host = config.get_item("tagger", "host")
    port = config.get_item("tagger", "port")
    app.run(debug=True, host=host, port=port)