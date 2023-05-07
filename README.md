# backify
Automatically backup my Spotify saved tracks and playlists.

> NOTE: `backify` only backs up only the relevant track details - track name, album and artists. It DOES NOT store any copyrighted music data or album art.

# How It Works?
`backify` uses `spotipy` to fetch the name, album and artists your saved tracks and playlists on a set interval (that is configurable) and saves them in a cheap data store (S3) as CSV files.

## Why Do This?
* A simple copy of your music library exists outside Spotify
* Music library is safe in case you:
    * lose access to your Spotify account irreversably
    * Accidentally delete all your liked songs and playlists
    * Delete your account without backing up your saved data first
* Decide to move away from Spotify to a different streaming service and want a the details of your music library

# Environment Variables

| Variable | Description |
| - | - |
| SPOTIPY_CLIENT_ID | The Spotify application Client ID obtained from the application dashboard |
| SPOTIPY_CLIENT_SECRET | The Spotify application Client secret obtained from the application dashboard |
| SPOTIPY_REDIRECT_URI | The Spotify application redirect URI. Must be the same as in the application configuration |
| SPOTIFY_MARKET | An `ISO 3166-1 alpha-2` country code to specify which market you are located in |
| AWS_ACCOUNT_ID | Your AWS Account ID |
| AWS_REGION | The AWS region to use for deployment of resources |
| BACKIFY_S3_BUCKET | The S3 bucket to save the backed up track data and Spotify access tokens|
| BACKUP_S3_BUCKET_FOLDER | The prefix under which to save the backed up track and playlist data in `BACKIFY_S3_BUCKET` |
| TOKENS_CACHE_S3_BUCKET_FOLDER | The prefix under which to save the access tokens in `BACKIFY_S3_BUCKET` |

# Spotify Developer API
* Auth: https://developer.spotify.com/documentation/general/guides/authorization/
* APIs: https://developer.spotify.com/documentation/web-api/reference

# Local Dev Env Setup

## Install `pipenv`
```bash
pip install pipenv --user
```
If the above doesn't work then:
```bash
sudo -H pip install -U pipenv
```

## Install Dependencies

```bash
pipenv install
```

## Switch to the `pipenv` venv
```bash
pipenv shell
```

## Exit from the `pipenv` venv
```bash
exit
```

## Build Lambda Container Image

```bash
docker build -t <tag> . \
    --build-arg SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID \
    --build-arg SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET \
    --build-arg SPOTIPY_REDIRECT_URI=$SPOTIPY_REDIRECT_URI \
    --build-arg SPOTIFY_MARKET=$SPOTIFY_MARKET \
    --build-arg BACKIFY_S3_BUCKET=$BACKIFY_S3_BUCKET \
    --build-arg BACKUP_S3_BUCKET_FOLDER=$BACKUP_S3_BUCKET_FOLDER \
    --build-arg TOKENS_CACHE_S3_BUCKET_FOLDER=$TOKENS_CACHE_S3_BUCKET_FOLDER
```

## Run Lambda Container Locally

```bash
docker run -p 8080:8080 <tag>
```

From another terminal instance:
```bash
curl -XPOST "http://localhost:8080/2015-03-31/functions/function/invocations" -d '{}'
```

## Build and Push Lambda Container Image to ECR

Login to ECR
```bash
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUND_ID.dkr.ecr.$AWS_REGION.amazonaws.com
```

Build, Tag and Push to ECR
```bash
./build-and-push.sh <tag>
```