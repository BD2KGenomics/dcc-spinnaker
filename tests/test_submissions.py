import json
import requests


def url_for(server, *args):
    """ Generate versions REST url """
    return "{}/v0/{}".format(server, "/".join(args))


def test_root(server):
    r = requests.get(server)
    assert(r.status_code == requests.codes.ok)


def test_submit(server):
    # create a submission
    r = requests.post(url_for(server, "submissions"),
                      json={"description": "foobar"})
    assert(r.status_code == requests.codes.created)
    submission = json.loads(r.text)["submission"]
    assert(submission['description'] == "foobar")

    # verify its there
    r = requests.get(url_for(server, "submissions/{}".format(submission["id"])))
    assert(submission["id"] == json.loads(r.text)["submission"]["id"])

    # Verify our submission is in the list of all submissions
    r = requests.get(url_for(server, "submissions"))
    assert(r.status_code == requests.codes.ok)
    assert(submission["id"] in [s["id"] for s in json.loads(r.text)["submissions"]])

    # Edit the submission
    r = requests.put(url_for(server, "submissions/{}".format(submission["id"])),
                     json={"description": "boodarg"})
    assert(r.status_code == requests.codes.ok)

    # verify its edited
    r = requests.get(url_for(server, "submissions/{}".format(submission["id"])))
    assert(json.loads(r.text)["submission"]["description"] == "boodarg")

    # delete it
    r = requests.delete(url_for(server, "submissions/{}".format(submission["id"])))
    assert(r.status_code == requests.codes.ok)

    # verify its deleted`
    r = requests.get(url_for(server, "submissions/{}".format(submission["id"])))
    assert(r.status_code != requests.codes.ok)
