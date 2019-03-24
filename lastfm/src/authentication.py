from pylast import LastFMNetwork, md5
import json

from lastfm import ROOT


def authenticate():
    with open(ROOT + '/credentials.json') as f:
        credentials = json.load(f)

    network = LastFMNetwork(api_key=credentials['API_key'],
                            api_secret=credentials['shared_secret'],
                            username=credentials['username'],
                            password_hash=md5(credentials['password']))
    return network
