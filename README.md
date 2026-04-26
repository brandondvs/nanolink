# NanoLink

A simple URL shortener service written in Python + FastAPI.

# Local Development

## Setup the virtualenv

Setup the virtual environment by running:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Launch containers

Make sure docker is installed on your machine and run:

```
docker compose up
```

## Start the dev server

Next, run the FastAPI server

```
fastapi dev
```

## Using Grafana

Grafana is installed as a docker container and is running by default at: localhost:3000.

The dashboards are saved to the local folder at `grafana/resources` and can be installed using the [GCX CLI](https://github.com/grafana/gcx).
You'll need to create a service account and generate a token to use with GCX. After you have the service account token, run the following:

```
gcx login
```

For the server enter: http://localhost:3000, then paste in the token value.

On Mac, the configuration file is stored at: ~/.config/gcx/config.yaml


Now push the local Grafana dashboard yaml to the server by running

```
gcx push dashboard -p grafana/resources
```

When complete there should be 3 dashboards listed now: NanoLink, Node Exporter Full, PostgreSQL Database
