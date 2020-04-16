import pytest
import json
from ssp.flask.api_endpoint.app import app as api_app


@pytest.fixture
def app():
    return api_app


def test_get_ner(client):
    mimetype = 'application/json'
    headers = {
        'Content-Type': mimetype,
        'Accept': mimetype
    }
    data = {
        "text" : "Wow! this is Wednesday night now and here the lazy Mageswaran coding me"
    }
    url = '/text/ner/spacy'

    response = client.post(url, data=json.dumps(data), headers=headers)
    res = response.json["res"]
    assert res == "{'TIME': 'Wednesday night', 'PERSON': 'Mageswaran'}"
