[![pipeline status](https://scm.cms.hu-berlin.de/callidus/machina-callida/badges/master/pipeline.svg)](https://scm.cms.hu-berlin.de/callidus/machina-callida/-/commits/master)
[![coverage report](https://scm.cms.hu-berlin.de/callidus/machina-callida/badges/master/coverage.svg)](https://scm.cms.hu-berlin.de/callidus/machina-callida/-/commits/master)
# Machina Callida
## Installation 
### Docker
1. Install Docker (https://docs.docker.com/v17.12/install/) and Docker-Compose (https://docs.docker.com/compose/install/).
2. Clone the repository:
    `git clone https://scm.cms.hu-berlin.de/callidus/machina-callida.git`.
3. Move to the newly created folder:
    `cd machina-callida`.
4. Run `docker-compose build`.
5. Run `docker-compose up -d`.

   When using the application for the first time, it may take a few minutes until the container "mc_frontend" has finished compiling the application.
6. Visit http://localhost:8100.

### Command line 
For installation via command line, see the respective subdirectories (`mc_frontend` and `mc_backend`).

## Debugging
### Access to the Docker container
Use `docker-compose down` to stop and remove the currently running containers.

To access a running container directly, get the container ID via `docker ps` and connect via `docker exec -it CONTAINER_ID bash`. Or, for root access, use: `docker exec -u 0 -it CONTAINER_ID bash`

Alternatively, you can use `ssh root@localhost -p 8022 -o "UserKnownHostsFile /dev/null"` to connect to the container via SSH. Password is "root".

To snapshot a running container, use `docker commit CONTAINER_ID`. It returns a snapshot ID, which you can access via `docker run -it SNAPSHOT_ID`.

## Models
To generate class structures for this project automatically: 
1. Install OpenAPI Generator (using, e.g., `brew install openapi-generator`).
2. Run: `openapi-generator generate -i mc_backend/mcserver/mcserver_api.yaml -g typescript-angular -o mc_frontend/openapi/ && openapi-generator generate -i mc_backend/mcserver/mcserver_api.yaml -g python-flask -o mc_backend/openapi/ && python mc_backend/openapi_generator.py`.

## Documentation
### API
To view the API documentation, visit https://korpling.org/mc-service/mc/api/v1.0/ui/ .
### Changelog
To update the changelog, use: `git log --oneline --decorate > CHANGELOG`

## Testing
### Locally
To test your code locally, run `./coverage_local.sh`
