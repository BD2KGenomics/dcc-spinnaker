import json
import requests


def url_for(server, *args):
    """ Generate versions REST url """
    return "{}/v0/{}".format(server, "/".join(args))


def test_root(server):
    r = requests.get(server)
    assert(r.status_code == requests.codes.ok)


def test_submit(server):
    r = requests.post(url_for(server, "submissions"),
                      json={"description": "foobar"})
    assert(r.status_code == requests.codes.ok)
    submission = json.loads(r.text)["submission"]
    assert(submission['description'] == "foobar")

    # Verify our submission is in the list of all submissions
    r = requests.get(url_for(server, "submissions"))
    assert(r.status_code == requests.codes.ok)
    assert(submission["id"] in [s["id"] for s in json.loads(r.text)["submissions"]])
