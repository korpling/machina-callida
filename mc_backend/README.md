[![pipeline status](https://scm.cms.hu-berlin.de/callidus/mc-backend/badges/master/pipeline.svg)](https://scm.cms.hu-berlin.de/callidus/mc-backend/commits/master)
[![coverage report](https://scm.cms.hu-berlin.de/callidus/mc-backend/badges/master/coverage.svg?job=coverage)](https://scm.cms.hu-berlin.de/callidus/mc-backend/commits/master)

# Installation instructions 
## Docker
1. Install Docker (https://docs.docker.com/v17.12/install/) and Docker-Compose (https://docs.docker.com/compose/install/)
2. Clone the repo:
    `git clone https://scm.cms.hu-berlin.de/callidus/mc_backend.git`
3. Move to the newly created folder:
    `cd mc_backend`
4. Run `docker-compose build`
5. Run `docker-compose up -d`

## No Docker
1. Set up a PostgreSQL database manually. If necessary, adjust the URI your .env file.
2. Run `python app.py` and `python run_csm.py` as separate processes.

## Endpoints
The default starting point for the API will be at http://localhost:5000/mc/api/v1.0/corpora .

----------------------------------------------------------------

# Configuration
For general configuration, use the file "mcserver/config.py".
To customize sensitive parts of your configuration, create a ".env" file in the directory "mcserver". A basic .env file may look like this:
```
DATABASE_URL_PROD=postgresql://postgres@db:5432/
DATABASE_URL=postgresql://postgres@db:5432/
\# Change this to "production" for public use
FLASK_ENV_VARIABLE=development
\# for Windows, use 127.0.0.1 instead
HOST_IP=0.0.0.0
RUST_BACKTRACE=1
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

----------------------------------------------------------------

# Dependencies
To update outdated dependencies, find the relevant ones by running: `pip list -o`

Then, for each of the listed dependencies, run: `pip install -U <DEPENDENCY_NAME>`

Or combine both commands in one line: `pip list -o --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U`

----------------------------------------------------------------

# Database
To autogenerate a new migration script, start the Docker container with the database and run: `flask db migrate`.

To migrate the database to a newer version manually, run: `flask db upgrade`

To migrate the database to a newer version manually, run: `flask db downgrade`

If it does nothing or fails, make sure that the environment variable FLASK_APP is set correctly (see https://flask.palletsprojects.com/en/1.1.x/cli/).

----------------------------------------------------------------

# Debugging
## Access to the Docker container
Use `docker-compose down` to stop and remove the currently running containers.

Use `ssh root@localhost -p 8022 -o "UserKnownHostsFile /dev/null"` to connect to the container via SSH. Password is "root".
Alternatively, get the container ID via `docker ps` and connect via `docker exec -it CONTAINER_ID bash`. Or, for root access, use: `docker exec -u 0 -it CONTAINER_ID bash`

To snapshot a running container, use `docker commit CONTAINER_ID`. It returns a snapshot ID, which you can access via `docker run -it SNAPSHOT_ID`.

----------------------------------------------------------------

# Testing
To check the coverage of the current tests, run
`coverage run --rcfile=.coveragerc tests.py && coverage combine && coverage report -m`.

----------------------------------------------------------------

# Documentation
## Changelog
To update the changelog, use: `git log --oneline --decorate --color > CHANGELOG`

