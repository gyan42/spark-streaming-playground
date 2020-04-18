#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import os
import shutil
from flask import Flask, render_template, request, url_for, jsonify
import gin

from ssp.posgress.dataset_base import PostgresqlConnection
from ssp.logger.pretty_print import print_error, print_info
from flask_paginate import Pagination, get_page_args

# https://gist.github.com/mozillazg/69fb40067ae6d80386e10e105e6803c9#file-index-html-L5
# https://github.com/doccano/doccano

PER_PAGE = 50

app = Flask(__name__)
app.debug = True

# STORE_PATH = os.path.expanduser("~") + "/ssp/text_tagger/"

@gin.configurable
class LabelsInfo(object):
    def __init__(self, labels=gin.REQUIRED):
        self.labels =labels


def check_n_mk_dirs(path, is_remove=False):
    if os.path.exists(path):
        if is_remove:
            shutil.rmtree(path)
    else:
        os.makedirs(path)


@app.route('/')
def index():
    """
    Home page with list of links for upload and download
    :return:
    """
    return render_template('layouts/index.html')


def get_subset(df, offset=0, per_page=PER_PAGE):
    return df.iloc[offset: offset + per_page]


@app.route('/tables_list', methods=['GET'])
def tables_list():
    try:
        db = PostgresqlConnection()
        tables_list = db.get_tables_list()
    except:
        return jsonify("No files found!")

    # remove extension
    data_files = [table for table in tables_list if table.startswith("test") or table.startswith("dev")]
    return render_template('layouts/dumped_tables_list.html', len=len(data_files), files=data_files)


@app.route('/tag_table/<table_name>', methods=['GET', 'POST'])
def tag_table(table_name):
    """
    Creates paginated pages, displaying text and corresponding lables
    :return:
    """
    db = PostgresqlConnection()
    df = db.query_to_df(f"select count(*) as count from {table_name}")
    total = df["count"].values[0]

    # Label dataframe, store the dictinaries
    labels = LabelsInfo()
    string_2_index = labels.labels
    index_2_string = dict(zip(string_2_index.values(), string_2_index.keys()))

    if request.method == 'POST':
        """
        Form is used to capture the text id, label and other pagination info.
        When `submit` is clicked we will get it as a POST request
        """
        print_info("===========================POST==============================")
        # Parse the response
        response = request.form.to_dict()
        print(response)

        page, per_page, offset = int(response["page"]), int(response["per_page"]), int(response["offset"])

        for i in range(offset, offset+PER_PAGE):
            j = str(i+1)
            index = int(response["id"+j])
            label = string_2_index[response["option"+j]]
            db.run_query(f"UPDATE {table_name} SET label={label} WHERE text_id={index}")
    else:
        page, _, _ = get_page_args(page_parameter='page',
                                   per_page_parameter='per_page')
        offset = PER_PAGE * (page-1)
        print_error([page, PER_PAGE, offset])

    data_df = db.query_to_df(f"select * from {table_name} ORDER BY text_id limit {PER_PAGE} offset {offset}")

    print_info(data_df[["text_id", "text"]])

    # Pagination, listing only a subset at a time
    pagination = Pagination(page=page,
                            per_page=PER_PAGE,
                            total=total,
                            css_framework='bootstrap4')

    print_error(data_df["text_id"].to_list())
    # Naive way of sending all the information to the HTML page and get it back in POST command
    return render_template('layouts/db_table_tagger.html',
                           page=page,
                           per_page=PER_PAGE,
                           offset=offset,
                           pagination=pagination,
                           file=table_name,
                           url=url_for("tag_table", table_name=table_name),
                           len=data_df.shape[0],
                           id=data_df["text_id"].to_list(),
                           text=data_df["text"].to_list(),
                           label=data_df["label"].to_list(),
                           label_string=[index_2_string[int(i)] for i in data_df["label"].to_list()],
                           options=list(string_2_index.keys()))

@gin.configurable
def tagger(host,
           port):
    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    gin.parse_config_file(config_file="config/tagger.gin")
    tagger()











# if __name__ == '__main__':
#     config = ConfigManager(config_path="config/config.ini")
#     host = config.get_item("tagger", "host")
#     port = config.get_item("tagger", "port")
#     app.run(debug=True, host=host, port=port)


# @app.route('/upload_data', methods=['GET', 'POST'])
# def upload_data():
#     """
#     Upload the user file into 'STORE_PATH'/data/ after deleting any old files in the path.
#     :return:
#     """
#     print("------")
#     if request.method == 'POST':
#         check_n_mk_dirs(path=STORE_PATH + "/data/", is_remove=False)
#         file: FileStorage = request.files.get('file')
#         print_error(file)
#         if "csv" in file.content_type:
#             df = pd.read_csv(file)
#             df.to_csv(STORE_PATH + "/data/" +file.filename)
#         elif "octet-stream" in file.content_type:
#             file.save(dst=STORE_PATH + "/data/" + file.filename)
#             df = pd.read_parquet(STORE_PATH + "/data/" + file.filename, engine="fastparquet")
#             # df.to_parquet(STORE_PATH + "/data/" + file.filename, engine="fastparquet")
#
#         return render_template('layouts/upload_data.html', count=df.shape[0], file=str(file.filename))
#     return render_template('layouts/upload_data.html', count=0, file="---")
#
#
# @app.route('/upload_labels', methods=['GET', 'POST'])
# def upload_labels():
#     """
#     Upload the user label file into 'STORE_PATH' after deleting any old files in the path.
#     :return:
#     """
#     if request.method == 'POST':
#         check_n_mk_dirs(path=STORE_PATH + "/labels/", is_remove=False)
#         file: FileStorage = request.files.get('file')
#         if "csv" in file.content_type:
#             df = pd.read_csv(file)
#             df.to_csv(STORE_PATH + "/labels/" + file.filename)
#         return render_template('layouts/upload_label.html', count=df.shape[0], file=str(file.filename))
#     return render_template('layouts/upload_label.html', count=0, file="---")



# @app.route('/uploaded_files_list', methods=['GET'])
# def uploaded_files_list():
#     try:
#         data_files = os.listdir(STORE_PATH + "/data/")
#     except:
#         return jsonify("No files found!")
#     # remove extension
#     data_files = [file.split(".")[0] for file in data_files]
#     return render_template('layouts/uploaded_files_list.html', len=len(data_files), files=data_files)
#

# @app.route('/tag_text/<file_name>', methods=['GET', 'POST'])
# def tag_text(file_name):
#     """
#     Creates paginated pages, displaying text and corresponding lables
#     :return:
#     """
#     data_file = file_name#data_files[0]
#     label_file = file_name+ "_label.csv"
#
#     # Open the file
#     try:
#         data_df = pd.read_csv(STORE_PATH + "/data/" + data_file + ".csv")
#     except:
#         data_df = pd.read_parquet(STORE_PATH + "/data/" + data_file + ".parquet", engine="fastparquet")
#
#     total = data_df.shape[0]
#     # reset the index and it starts with 0
#     data_df = data_df.reset_index(drop=True)
#
#     # Type cast the columns as required
#     data_df["id"] = data_df["id"].fillna(0).astype(int)
#     data_df["label"] = data_df["label"].fillna(0).astype(int)
#
#     # Label dataframe, store the dictinaries
#     label_df = pd.read_csv(STORE_PATH + "/labels/" + label_file)
#     label_df["index"] = label_df["index"].astype(int)
#     string_2_index = dict(zip(label_df["label"], label_df["index"]))
#     index_2_string = dict(zip(string_2_index.values(), string_2_index.keys()))
#
#     if request.method == 'POST':
#         """
#         Form is used to capture the text id, label and other pagination info.
#         When `submit` is clicked we will get it as a POST request
#         """
#         print_info("===========================POST==============================")
#         # Parse the response
#         response = request.form.to_dict()
#         # {'id': '11', 'label': '0', 'page': '2', 'per_page': '10', 'offset': '10', 'option': 'NATURE', 'sumbit': 'Submit'}
#         print(response)
#         page, per_page, offset = int(response["page"]), int(response["per_page"]), int(response["offset"])
#
#         for i in range(offset, offset+PER_PAGE):
#
#             # Update the Dataframe
#             index = int(response["id"+str(i)])
#
#             # check whether id col start with 1 or 0
#             # if id start with 1, then it needs to be adjusted to index which starts with 0
#             if data_df.shape[0] == data_df["id"].to_list()[-1]:
#                 index = index - 1
#             data_df.at[index, "label"] = string_2_index[response["option"+str(i)]]
#
#         # Write the updated DataFrame
#         if "csv" in data_file:
#             data_df.to_csv(STORE_PATH + "/data/" + data_file, index=False)
#         elif "parquet" in data_file:
#             data_df.to_parquet(STORE_PATH + "/data/" + data_file, engine="fastparquet")
#
#         # move the page to the updated Text form
#         # scroll_id = response["id"]
#     else:
#         page, _, _ = get_page_args(page_parameter='page',
#                                    per_page_parameter='per_page')
#         # No updates and hence to scrolling
#         # scroll_id = None
#         per_page = PER_PAGE #per_page #TODO better way
#         offset = per_page * (page-1)
#         print_error([page, per_page, offset])
#
#     data_df = get_subset(df=data_df, offset=offset, per_page=per_page)
#
#     # Pagination, listing only a subset at a time
#     pagination = Pagination(page=page,
#                             per_page=per_page,
#                             total=total,
#                             css_framework='bootstrap4')
#
#     print_error(data_df["id"].to_list())
#     # Naive way of sending all the information to the HTML page and get it back in POST command
#     return render_template('layouts/tagger.html',
#                            # scroll_id=scroll_id,
#                            page=page,
#                            per_page=per_page,
#                            offset=offset,
#                            pagination=pagination,
#                            file=data_file,
#                            url=url_for("tag_text", file_name=file_name),
#                            len=data_df.shape[0],
#                            id=data_df["id"].to_list(),
#                            text=data_df["text"].to_list(),
#                            label=data_df["label"].to_list(),
#                            label_string=[index_2_string[int(i)] for i in data_df["label"].to_list()],
#                            options=list(string_2_index.keys()))
#

# @app.route('/download_files_list', methods=['GET'])
# def download_files_list():
#     try:
#         data_files = os.listdir(STORE_PATH + "/data/")
#     except:
#         return jsonify("No files found!")
#     # remove extension
#     data_files = [file.split(".")[0] for file in data_files]
#     return render_template('layouts/download_files_list.html', len=len(data_files), files=data_files)
#
#
# @app.route('/download/<file_name>', methods=['GET', 'POST'])
# def download(file_name):
#     data_files = os.listdir(STORE_PATH + "/data/")
#     for actual_name in data_files:
#         if file_name in actual_name:
#             file = actual_name
#     return send_file(STORE_PATH + "/data/" + file, as_attachment=True)
