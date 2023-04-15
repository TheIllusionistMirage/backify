"""
Generate Spotify access token
"""

from os import getenv, remove
import sys
import json
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler

from backify.s3_helper import S3Helper


TOKEN_CACHE_PATH = './.tokens/token-cache.json'


def authenticate_and_create_first_token():
    print(
        f'Authenticating & saving tokens for the Spotify app with ID: {getenv("SPOTIPY_CLIENT_ID")}...')

    try:
        spotify_client = Spotify(
            auth_manager=SpotifyOAuth(
                open_browser=True,
                scope='playlist-read-private,user-library-read',
                cache_handler=CacheFileHandler(cache_path=TOKEN_CACHE_PATH)
            )
        )

        print(spotify_client.me())

        print(
            f'Successfully authenticated & saving tokens for the Spotify app with ID: {getenv("SPOTIPY_CLIENT_ID")} to {TOKEN_CACHE_PATH}')
    except Exception as e:
        print(
            f'Unable to authenticate and save access tokens to {TOKEN_CACHE_PATH}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(
            f'Usage: {sys.argv[0]} <backify-s3-bucket> <tokens-cache-s3-bucket-folder>')
        exit(1)

    backify_s3_bucket = sys.argv[1]
    tokens_cache_s3_bucket_folder = sys.argv[2]

    authenticate_and_create_first_token()

    with open(TOKEN_CACHE_PATH, 'r') as f:
        data = json.loads(f.read())

    if not data:
        print(
            f'Unable to copy cached token data to token cache on s3://{backify_s3_bucket}/{tokens_cache_s3_bucket_folder}/token-cache.json')
        exit(1)

    S3Helper.save_json_file_data(
        backify_s3_bucket, tokens_cache_s3_bucket_folder, 'token-cache.json', data)
    print(
        f'Copied cached token data to token cache on s3://{backify_s3_bucket}/{tokens_cache_s3_bucket_folder}/token-cache.json')

    print(f'Deleting local token cache \'{TOKEN_CACHE_PATH}\'...')
    remove(TOKEN_CACHE_PATH)
    print(f'Deleted local token cache \'{TOKEN_CACHE_PATH}\'')
