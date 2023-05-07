#!/bin/bash

lambda_container_image_name="$1"
lambda_container_image_tag="$2"
spotify_client_id="$3"
spotify_client_secret="$4"
spotify_redirect_uri="$5"
spotify_market="$6"
backify_s3_bucket="$7"
backup_s3_bucket_folder="$8"
tokens_cache_s3_bucket_folder="$9"
aws_account_id="${10}"
aws_region="${11}"

echo "* Logging into ECR..."
aws ecr get-login-password \
    --region $aws_region | docker login --username AWS --password-stdin $aws_account_id.dkr.ecr.$aws_region.amazonaws.com > /dev/null

if [ "$?" -ne 0 ]; then
    echo "** Failed to log into ECR for AWS Account '$aws_account_id' and region '$aws_region'"
    exit 1
else
    echo "** Logged into ECR"
fi

echo "* Building container '$lambda_container_image_name:$lambda_container_image_tag'..."
docker build -t $lambda_container_image_name:$lambda_container_image_tag . \
    --build-arg SPOTIPY_CLIENT_ID=$spotify_client_id \
    --build-arg SPOTIPY_CLIENT_SECRET=$spotify_client_secret \
    --build-arg SPOTIPY_REDIRECT_URI=$spotify_redirect_uri \
    --build-arg SPOTIFY_MARKET=$spotify_market \
    --build-arg BACKIFY_S3_BUCKET=$backify_s3_bucket \
    --build-arg BACKUP_S3_BUCKET_FOLDER=$backup_s3_bucket_folder \
    --build-arg TOKENS_CACHE_S3_BUCKET_FOLDER=$tokens_cache_s3_bucket_folder

echo "** Built container '$lambda_container_image_name:$lambda_container_image_tag'"

echo "* Tagging container '$lambda_container_image_name:$lambda_container_image_tag'..."
docker \
    tag $lambda_container_image_name:$lambda_container_image_tag \
    $aws_account_id.dkr.ecr.$aws_region.amazonaws.com/$lambda_container_image_name:$lambda_container_image_tag
echo "** Tagged container '$lambda_container_image_name:$lambda_container_image_tag'"

echo "* Pushing container '$lambda_container_image_name:$lambda_container_image_tag'..."
docker push \
    $aws_account_id.dkr.ecr.$aws_region.amazonaws.com/$lambda_container_image_name:$lambda_container_image_tag
echo "* Pushed container '$lambda_container_image_name:$lambda_container_image_tag'"

echo "* Finished uploading Lambda container image '$lambda_container_image_name:$lambda_container_image_tag'"
