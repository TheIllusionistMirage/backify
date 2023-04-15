"""
S3 based token cache handler.
"""

from spotipy.cache_handler import CacheHandler

from backify.s3_helper import S3Helper


class S3CacheHandler(CacheHandler):
    """
    S3 Spotipy token cache helper.
    """

    def __init__(self, bucket: str, prefix: str, cache_file_name: str):
        self.bucket = bucket
        self.prefix = prefix
        self.cache_file_name = cache_file_name

    def get_cached_token(self):
        """
        Get and return a token_info dictionary object.
        """
        return S3Helper.get_json_file_data(self.bucket, self.prefix, self.cache_file_name)

    def save_token_to_cache(self, token_info):
        """
        Save a token_info dictionary object to the cache and return None.
        """
        S3Helper.save_json_file_data(
            self.bucket, self.prefix, self.cache_file_name, token_info)
