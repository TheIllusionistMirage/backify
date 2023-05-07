"""
Application Exceptions.
"""


class S3ReadWriteError(Exception):
    """
    Unable to read or write files from S3
    """

    def __init__(self, msg: str, bucket: str, prefix: str, file_name: str):
        self.msg = msg
        self.bucket = bucket
        self.prefix = prefix
        self.file_name = file_name
