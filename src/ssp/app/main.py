#https://www.javacodemonk.com/named-entity-recognition-spacy-flask-api-1678a5df
from flask import Flask, request, abort, jsonify
import spacy

from ssp.utils.config_manager import ConfigManager

nlp = spacy.load('en_core_web_sm')

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/spacy/api/v0.1/ner', methods=["POST"])
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


if __name__ == '__main__':
    config = ConfigManager(config_path="config.ini")
    host = config.get_item("api", "host")
    port = config.get_item("api", "port")
    app.run(debug=True, host=host, port=port)
