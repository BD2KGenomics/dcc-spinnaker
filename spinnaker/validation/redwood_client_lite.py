import requests

# A lightweight client that calls a redwood server API
# to download small files or parts of larger files.

# Two kinds of downloading :
# download an entire json file and return the contents as json
# download a partial file of any type and return the bytes


# Downloads an entire object and returns it as json
# redwood_storage_url : eg https://storage2.ucsc-cgl.org:5431
# object_id : uuid of the object
# redwood_key : key for the redwood storage server (not an AWS key)
def download_json(redwood_storage_url, object_id, redwood_key):
    # Talk to the redwood server and get an aws signed URL for the passed-in object_id
    parameters = {'offset': '0', 'length': '-1', 'external': 'true'}
    url = '%s/download/%s' % (redwood_storage_url, object_id)
    header = {'AUTHORIZATION': 'Bearer %s' % redwood_key}
    # TODO  specify a timeout to prevent server from potentially hanging forever in prod mode
    redwood_response = requests.get(url, headers=header, params=parameters)
    # TODO error-checking - make sure all these bits actually exist
    aws_url = redwood_response.json()['parts'][0]['url']

    # Get the passed object in its entirety
    aws_response = requests.get(aws_url)

    print aws_response.json()

    return aws_response.json()


# TODO NYI
# Download the beginning of an arbitrary binary file as specified by range_len
# and return it as bytes.
def download_partial_file(redwood_storage_url, object_id, redwood_key, range_len):
    return "NYI"


def main(*args):
    download_json(*args)


if __name__ == "__main__":
    main()
