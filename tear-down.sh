#!/bin/bash

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


echo "* Tear down backify v$backify_version..."
echo "* Gather deployment details:-"

printf "** Enter AWS Account ID: "
read aws_account_id

printf "** Enter AWS region: "
read aws_region

printf "** Enter bucket name for backify: "
read backify_s3_bucket

printf "* Retain bucket '$backify_s3_bucket'? (yes/no) (IMPORTANT: If you select no, all backups will be gone, forever!): "
read retain_backify_s3_bucket

echo "* Tear down details"
echo "** AWS Account ID: $aws_account_id"
echo "** AWS region: $aws_region"
echo "** Backify S3 bucket: $backify_s3_bucket"
echo "** Retaining Backify S3 bucket?: $retain_backify_s3_bucket"

printf "* Proceed with teardown? (yes/no) (IMPORTANT: There's no turning back after this!): "
read proceed

if [ "$proceed" = "yes" ]; then
    ecr_repo_name="backify"
    backify_stack_name="backify-cf-stack"

    echo "Deleting AWS resources..."

    aws cloudformation delete-stack \
        --stack-name $backify_stack_name \
        --region $aws_region

    aws ecr delete-repository \
        --repository-name $ecr_repo_name \
        --force \
        --region $aws_region
    
    if [ "$retain_backify_s3_bucket" = "no" ]; then
        aws s3 rm s3://mybucket --recursive
    fi

    echo "Finished deleting AWS resources"
else
    echo "You changed your mind, aborting teardown."
    printf "\nAll done, KTHXBYE! ;)"
fi
