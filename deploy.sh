#!/bin/bash

backify_version=$(cat version.json | tr -d '"')

echo " ___                          ___                 .-.                "
echo "(   )                        (   )         .-.   /    \\              "
echo " | |.-.     .---.    .--.     | |   ___   ( __)  | .\`. ;   ___  ___  "
echo " | /   \\   / .-, \\  /    \\    | |  (   )  (''\\\")  | |(___) (   )(   ) "
echo " |  .-. | (__) ; | |  .-. ;   | |  ' /     | |   | |_      | |  | |  "
echo " | |  | |   .'\`  | |  |(___)  | |,' /      | |  (   __)    | |  | |  "
echo " | |  | |  / .'| | |  |       | .  '.      | |   | |       | '  | |  "
echo " | |  | | | /  | | |  | ___   | | \`. \\     | |   | |       '  \`-' |  "
echo " | '  | | ; |  ; | |  '(   )  | |   \\ \\    | |   | |        \`.__. |  "
echo " ' \`-' ;  ' \`-'  | '  \`-' |   | |    \\ .   | |   | |        ___ | |  "
echo "  \`.__.   \`.__.'_.  \`.__,'   (___ ) (___) (___) (___)      (   )' |  "
echo "                                                            ; \`-' '  "
echo "                                                             .__.'   "


echo "* Deploying backify v$backify_version..."
echo "* Gather deployment details:-"

printf "** Enter AWS Account ID: "
read aws_account_id

printf "** Enter AWS region: "
read aws_region

printf "** Enter Spotify application client ID: "
read spotify_app_client_id

printf "** Enter Spotify application client secret: "
read spotify_app_client_secret

printf "** Enter Spotify redirect URI: "
read spotify_redirect_uri

printf "** Spotify market (should be valid ISO 3166-1 alpha-2 code): "
read spotify_market

printf "** Enter bucket name for backify: "
read backify_s3_bucket

printf "** Enter backup folder name: "
read backup_s3_bucket_folder

printf "** Enter tokens cache folder name: "
read tokens_cache_s3_bucket_folder

printf "** Enter backup frequency (in days): "
read backup_frequency_in_days

ecr_repo_name="backify"
echo "* Creating ECR repository '$ecr_repo_name'..."
echo "** Checking if ECR repository '$ecr_repo_name' already exists..."
exists="$(aws ecr describe-repositories --region $aws_region --repository-names $ecr_repo_name --query repositories[0].repositoryName 2>&1 | tr -d '"' )"

if [ "$exists" = "$ecr_repo_name" ]; then
    echo "** ECR repository '$ecr_repo_name' already exists"
else
    echo "** ECR repository '$ecr_repo_name' does not exist, creating..."
    aws ecr create-repository \
        --repository-name $ecr_repo_name \
        --image-tag-mutability IMMUTABLE \
        --region $aws_region > /dev/null
    echo "** Created ECR repository '$ecr_repo_name'"
fi

printf "* Enter Lambda container image tag to use: "
read lambda_container_image_tag

lambda_container_image_name="backify"

./build-and-push.sh \
    $lambda_container_image_name \
    $lambda_container_image_tag \
    $spotify_app_client_id \
    $spotify_app_client_secret \
    $spotify_redirect_uri \
    $spotify_market \
    $backify_s3_bucket \
    $backup_s3_bucket_folder \
    $tokens_cache_s3_bucket_folder \
    $aws_account_id \
    $aws_region

backify_stack_name="backify-cf-stack"
echo "* Deploying backify CF stack '$backify_stack_name'..."

stack_id="$(aws cloudformation create-stack \
    --template-body file://cf-template.yaml \
    --stack-name $backify_stack_name \
    --parameters ParameterKey=BackifyS3BucketName,ParameterValue=$backify_s3_bucket ParameterKey=BackupS3BucketFolder,ParameterValue=$backup_s3_bucket_folder ParameterKey=TokensCacheS3BucketFolder,ParameterValue=$tokens_cache_s3_bucket_folder ParameterKey=LambdaContainerImageName,ParameterValue=$lambda_container_image_name ParameterKey=LambdaContainerImageTag,ParameterValue=$lambda_container_image_tag ParameterKey=BackupFrequencyInDays,ParameterValue=$backup_frequency_in_days \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --region $aws_region \
    --query StackId | tr -d '\"')"

if [ "$?" -ne 0 ]; then
    echo "** Failed to initiate CF stack creation"
    exit 1
fi

echo "** Waiting for stack creation ('$stack_id') to complete..."

aws cloudformation wait stack-create-complete \
    --stack-name "$stack_id" \
    --region $aws_region

echo "** Stack creation completed"

echo "** Finished deploying backify CF stack '$backify_stack_name'"

echo "* Authenticating to Spotfy app for the current Spotify user..."
python authenticator.py $backify_s3_bucket $tokens_cache_s3_bucket_folder

if [ "$?" -ne 0 ]; then
    echo "** Failed to authenticate Spotify app for the current Spotify user"
    exit 1
else
    echo "** Finished authenticating Spotify app for the current Spotify user"
fi

echo "* Finished deploying backify! Backup will run every $backup_frequency_in_days days"
printf "* Do you want to run backify now? (yes/no): "
read run_now

if [ "$run_now" = "yes" ]; then
    echo "** Running backify now..."
    aws lambda invoke \
        --function-name backify \
        --invocation-type RequestResponse \
        --payload {} \
        --region $aws_region \
        response.json
    echo "** Finished running backify"
    rm response.json
fi

printf "\nAll done, KTHXBYE! ;)"
