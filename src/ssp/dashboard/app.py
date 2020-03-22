from flask import Flask, render_template

import json
import plotly
from ssp.utils.config_manager import ConfigManager
from ssp.utils.postgresql import postgressql_connection, create_pandas_table

app = Flask(__name__)
app.debug = True



@app.route('/')
def index():
    return render_template('layouts/index.html')

@app.route('/trending_tags')
def trending_tags():
    config = ConfigManager(config_path="config.ini")
    postgresql_host = config.get_item("postgresql", "host")
    postgresql_port = config.get_item("postgresql", "port")
    postgresql_database = config.get_item("postgresql", "database")
    postgresql_user = config.get_item("postgresql", "user")
    postgresql_password = config.get_item("postgresql", "password")

    conn = postgressql_connection(postgresql_host, postgresql_port, postgresql_database, postgresql_user, postgresql_password)
    df = create_pandas_table("select * from trending_hashtags", database_connection=conn)

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


if __name__ == '__main__':
    config = ConfigManager(config_path="config.ini")
    host = config.get_item("dashboard", "host")
    port = config.get_item("dashboard", "port")
    app.run(debug=True, host=host, port=port)