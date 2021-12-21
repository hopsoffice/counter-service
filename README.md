# Counter Service

Simple number counting service with HTTP API

## Prerequisite

- Python 3.10
- SQLite

## Installation

```console
$ pip install poetry
$ poetry install
$ ln -s ../../hooks/pre-commit .git/hooks
$ mkdir db
```

## Run

```console
$ python app.py
```

## Docker

### Build

```console
$ docker build . -t counter
```

### Run

```console
$ export COUNTER_DATABASE_PATH=/your/database/path
$ docker run -p 8000:8000 --rm -v "$COUNTER_DATABASE_PATH:/app/db" counter
```
