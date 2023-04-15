from os import getenv
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from backify.fetch_spotify_data import SpotifyDataHelper
from backify.s3_helper import S3Helper


class Backup:
    def __init__(self):
        self.spotify_data_helper = SpotifyDataHelper()

    def backup_all(self):
        backup_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.backup_saved_tracks(backup_name)
        self.backup_playlists(backup_name)

    def backup_saved_tracks(self, backup_name: str):
        print('Backing up saved tracks...')

        saved_tracks = self.spotify_data_helper.fetch_saved_tracks()
        S3Helper.save_csv_file_data(
            getenv('BACKIFY_S3_BUCKET'),
            f'{getenv("BACKUP_S3_BUCKET_FOLDER")}/{backup_name}',
            'saved_tracks.csv',
            saved_tracks,
            ['track_name', 'artists', 'album'])

        print('Finished backing up saved tracks')

    def backup_playlists(self, backup_name: str):
        print('Backing up playlists...')

        playlists = self.spotify_data_helper.fetch_playlists()
        for playlist_name, playlist_tracks in playlists:
            S3Helper.save_csv_file_data(
                getenv('BACKIFY_S3_BUCKET'),
                f'{getenv("BACKUP_S3_BUCKET_FOLDER")}/{backup_name}/playlists',
                f'{playlist_name}.csv',
                playlist_tracks,
                ['track_name', 'artists', 'album'])

        print('Finished backing up playlists')
