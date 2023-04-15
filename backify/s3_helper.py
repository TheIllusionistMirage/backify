from typing import Any
import json
import csv
import io
import boto3

from backify.error import S3ReadWriteError


class S3Helper:
    """
    Wrapper on top of the boto3 S3 client to get/put JSON files on S3
    """

    client = boto3.client('s3', region_name='us-east-1')

    @staticmethod
    def get_json_file_data(bucket: str, prefix: str, file_name: str) -> Any:
        """
        Get the data of a JSON file from S3.

        ### Args
        * `bucket (str)`: Name of the S3 bucket to read the file from
        * `prefix (str)`: The prefix to use
        * `file_name (str)`: The file name (with extension) to read and parse as a JSON
        """
        get_obj_res = S3Helper.client.get_object(
            Bucket=bucket, Key=f'{prefix}/{file_name}')

        if not get_obj_res or not get_obj_res['Body'] or \
                get_obj_res['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise S3ReadWriteError(
                f'Unable to read file: s3://{bucket}/{prefix}/{file_name}',
                bucket, prefix, file_name)

        return json.load(get_obj_res['Body'])

    @staticmethod
    def save_json_file_data(bucket: str, prefix: str, file_name: str, data: Any):
        """
        Save data as a JSON file on S3.

        ### Args
        * `bucket (str)`: Name of the S3 bucket to read the file from
        * `prefix (str)`: The prefix to use
        * `file_name (str)`: The file name (with extension) to read and parse as a JSON
        * `data (Any)`: The data to write to S3
        """
        put_obj_res = S3Helper.client.put_object(
            Bucket=bucket, Key=f'{prefix}/{file_name}',
            Body=bytes(json.dumps(data), encoding='utf-8'))

        if not put_obj_res or not put_obj_res['ResponseMetadata'] or \
                put_obj_res['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise S3ReadWriteError(
                f'Unable to write S3 file: s3://{bucket}/{prefix}/{file_name}',
                bucket, prefix, file_name)

    @staticmethod
    def save_csv_file_data(bucket: str, prefix: str, file_name: str, data: list, field_names: list):
        """
        Save data as a CSV file on S3.

        ### Args
        * `bucket (str)`: Name of the S3 bucket to read the file from
        * `prefix (str)`: The prefix to use
        * `file_name (str)`: The file name (with extension) to read and parse as a JSON
        * `data (Any)`: The data to write to S3
        """
        csv_data = None

        with io.StringIO(newline='\n') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)

            writer.writeheader()
            writer.writerows(data)

            csv_data = csv_file.getvalue()
            csv_file.close()

        put_obj_res = S3Helper.client.put_object(
            Bucket=bucket, Key=f'{prefix}/{file_name}',
            Body=bytes(csv_data, encoding='utf-8'))

        if not put_obj_res or not put_obj_res['ResponseMetadata'] or \
                put_obj_res['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise S3ReadWriteError(
                f'Unable to write S3 file: s3://{bucket}/{prefix}/{file_name}',
                bucket, prefix, file_name)
