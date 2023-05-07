from os import getenv
from time import sleep
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from backify.token_cache_handler import S3CacheHandler


class SpotifyDataHelper:
    def __init__(self):
        self.spotify_client = Spotify(
            auth_manager=SpotifyOAuth(
                open_browser=False,
                scope='playlist-read-private,user-library-read',
                cache_handler=S3CacheHandler(
                    bucket=getenv('BACKIFY_S3_BUCKET'),
                    prefix=getenv('TOKENS_CACHE_S3_BUCKET_FOLDER'),
                    cache_file_name='token-cache.json')
            )
        )

    def fetch_saved_tracks(self):
        print('Fetching saved tracks')

        limit = 50
        offset = 0
        market = getenv('SPOTIFY_MARKET')
        tracks_fetched = 0
        total_saved_tracks = None
        saved_tracks = []

        while True:
            saved_tracks_res = self.spotify_client.current_user_saved_tracks(
                offset=offset, limit=limit, market=market)

            if not total_saved_tracks:
                total_saved_tracks = saved_tracks_res['total']

            tracks_fetched += len(saved_tracks_res['items'])
            saved_tracks.extend([
                {
                    'track_name': track_data['track']['name'],
                    'artists': ','.join([artist['name'] for artist in track_data['track']['artists']]),
                    'album': track_data['track']['album']['name']
                } for track_data in saved_tracks_res['items'] if track_data['track']
            ])

            offset += limit

            # No more saved tracks to fetch
            if not saved_tracks_res['next'] or tracks_fetched == total_saved_tracks:
                break

            sleep(0.2)

        print(f'Total tracks fetched: {tracks_fetched}')
        print('Finished fetching saved tracks')

        return saved_tracks

    def fetch_playlists(self):
        def _valid_char(char):
            return char != '/' and char != '\\'

        print('Fetching playlists...')

        limit = 50
        offset = 0
        playlists_fetched = 0
        total_playlists = None
        playlists = []
        untitled_playlist_id = 1

        while True:
            playlists_res = self.spotify_client.current_user_playlists(
                limit=limit, offset=offset)

            if not total_playlists:
                total_playlists = playlists_res['total']

            playlists_fetched += len(playlists_res['items'])

            playlist_info = [
                {
                    'id': playlist_data['id'],
                    'name': playlist_data['name']
                } for playlist_data in playlists_res['items']
            ]

            for playlist in playlist_info:
                playlist_name: str
                if playlist['name']:
                    playlist_name = ''.join(
                        ch if _valid_char(ch) else ' ' for ch in playlist['name'])
                else:
                    playlist_name = f'untitled-{untitled_playlist_id}'
                    untitled_playlist_id += 1

                playlists.append((playlist_name, self.fetch_tracks_in_playlist(
                    playlist['id'], playlist_name)))

            # No more playlists to fetch
            if not playlists_res['next'] or playlists_fetched == total_playlists:
                break

            offset += limit

            sleep(0.2)

        print(f'Total playlists fetched: {playlists_fetched}')
        print('Finished fetching playlists')

        return playlists

    def fetch_tracks_in_playlist(self, playlist_id: str, playlist_name: str):
        print(f'Fetching tracks in playlist: {playlist_name}...')

        limit = 50
        offset = 0
        tracks_fetched = 0
        total_tracks = None
        playlist_items = []

        while True:
            playlist_data_res = self.spotify_client.playlist_items(
                playlist_id=playlist_id, offset=offset, limit=limit,
                fields='items(track(name,album(name),artists(name))),next,total,limit,offset')
            playlist_items.extend([{
                'track_name': track_data['track']['name'],
                'artists': ','.join([artist['name'] for artist in track_data['track']['artists']]),
                'album': track_data['track']['album']['name']
            } for track_data in playlist_data_res['items'] if track_data['track']])

            # No more tracks to fetch
            if not playlist_data_res['next'] or tracks_fetched == total_tracks:
                break

            offset += limit
            sleep(0.2)

        print(f'Finished fetching tracks in playlist: {playlist_name}')
        return playlist_items
