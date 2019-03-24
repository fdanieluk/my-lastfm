from pylast import LastFMNetwork, md5
import json
from os.path import join
from datetime import datetime
from glob import glob
import pandas as pd


from lastfm import ROOT


RAW_DATA = join(ROOT, 'data', 'raw')
PROCESSED_DATA = join(ROOT, 'data', 'processed')


def authenticate():
    credentials_path = join(ROOT, 'credentials.json')
    with open(credentials_path) as f:
        credentials = json.load(f)

    network = LastFMNetwork(api_key=credentials['API_key'],
                            api_secret=credentials['shared_secret'],
                            username=credentials['username'],
                            password_hash=md5(credentials['password']))
    return network


def download_tracks(user):
    time_to = int(datetime.timestamp(datetime.now()))
    # time_to = 1349518435

    i = 0
    while True:
        print(f'Downloading tracks up to: {datetime.fromtimestamp(time_to)}')
        tracks = user.get_recent_tracks(limit=1000,
                                        time_to=time_to)
        # get time of last track downloaded in this batch
        try:
            time_to = int(tracks[-1][3])
        except IndexError:
            # last file
            break

        date_ = datetime.fromtimestamp(time_to)
        date_ = date_.__str__().replace(':', '').replace('-', '').replace(' ', '_')  # yes i did it

        my_tracks = []
        for track in tracks:
            track_info = {'title': track[0].title,
                          'album': track[1],
                          'artist': track[0].artist.name,
                          'timestamp': track[3]}
            my_tracks.append(track_info)

        data = json.dumps(my_tracks)
        save_path = join(RAW_DATA, f'tracks_since{date_}.json')
        i += 1
        with open(save_path, 'w') as outfile:
            json.dump(data, outfile)


def tabularize_data():
    files = glob(f'{RAW_DATA}/*.json', recursive=True)

    to_concat = []
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)
        data = json.loads(data)
        to_concat.append(pd.DataFrame(data))

    df = pd.concat(to_concat)

    df = df.reset_index(drop=True)
    df.timestamp = df.timestamp.astype(int)
    df.query('timestamp > 1293836400')  # 1293836400 = datetime(2011, 1, 1) 

    save_path = join(PROCESSED_DATA, 'lastfm-tracks.csv')
    df.to_csv(save_path)


def main():
    network = authenticate()
    user = network.get_user('imintogoodmusic')
    download_tracks(user)
    tabularize_data()


if __name__ == '__main__':
    main()
