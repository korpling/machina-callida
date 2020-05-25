# Installing the backend via command line
1. Set up a PostgreSQL database manually (https://www.postgresql.org/download/). If necessary, adjust the URI in your .env file located at `mcserver/.env`.
2. Run `pip install -r requirements.txt`.
3. Run `python app.py` and `python run_csm.py` as separate processes.

## Endpoints
The default starting point for the API will be at http://localhost:5000/mc/api/v1.0/corpora .

----------------------------------------------------------------

# Configuration
For general configuration, use the file `mcserver/config.py`.
To customize sensitive parts of your configuration, create a ".env" file in the directory "mcserver". A basic .env file may look like this:
```
DATABASE_URL_PROD=postgresql://postgres@db:5432/
DATABASE_URL=postgresql://postgres@db:5432/
# Change this to "production" for public use
FLASK_ENV_VARIABLE=development
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
To autogenerate a new migration script:
1. Start the Docker container with the database: `docker-compose run -p 5432:5432 -d db`
2. Create a new migration: `flask db migrate`.
3. Perform a migration... 
    - ... to a newer version: `flask db upgrade`.
    - ... to an older version: `flask db downgrade`.
    - If it does nothing or fails, make sure that the environment variable FLASK_APP is set correctly (see https://flask.palletsprojects.com/en/1.1.x/cli/): `export FLASK_APP=app.py`
5. To finish the process, shut down the database container: `docker-compose down`

----------------------------------------------------------------

# Models
To generate class structures for this project automatically: 
1. Install OpenAPI Generator (using, e.g., `brew install openapi-generator`).
2. Run: `openapi-generator generate -i ./mcserver/mcserver_api.yaml -g python-flask -o ./openapi/ && python openapi_generator.py`.
# Testing
To check the coverage of the current tests, run
`coverage run --rcfile=.coveragerc tests.py && coverage combine && coverage report -m`.
