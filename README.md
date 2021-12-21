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

## Usage

### Request to count

You can count number with memo.

```console
$ curl -X POST localhost:8000/count/ --data '{"memo": "initial"}'
{"success":true,"data":{"number":1,"memo":"initial"}}
```

Or you can without memo too.

```console
$ curl -X POST localhost:8000/count/
{"success":true,"data":{"number":2,"memo":null}}
```

### Set start number (optional)

To set start number, you sholud manually update database's value.

```console
$ sqlite db/counter.db
SQLite version 3.7.17 2013-05-20 00:56:22
Enter ".help" for instructions
Enter SQL statements terminated with a ";"
sqlite> UPDATE SQLITE_SEQUENCE SET seq = 977 WHERE name = 'cnt';
sqlite>
```

Then it counts from the number after the number you choose.

```console
$ curl -X POST localhost:8000/count/
{"success":true,"data":{"number":978,"memo":null}}
```
