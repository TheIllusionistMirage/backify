# backify
Automatically backup my Spotify playlists

# Local Dev env Setup

## Install `pipenv`
```bash
$ pip install pipenv --user
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

# Run Tests

## Run Unit Test
```bash
python -m tox
```