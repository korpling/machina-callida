[![pipeline status](https://scm.cms.hu-berlin.de/callidus/mc_frontend/badges/master/pipeline.svg)](https://scm.cms.hu-berlin.de/callidus/mc_frontend/-/commits/master)
[![coverage report](https://scm.cms.hu-berlin.de/callidus/mc_frontend/badges/master/coverage.svg)](https://scm.cms.hu-berlin.de/callidus/mc_frontend/-/commits/master)
# Installation 
## via Docker:
1. Install Docker (https://docs.docker.com/v17.12/install/) and Docker-Compose (https://docs.docker.com/compose/install/)
2. Clone the repo:
    `git clone https://scm.cms.hu-berlin.de/callidus/mc_frontend.git`
3. Move to the newly created folder:
    `cd mc_frontend`
4. Make sure to assign at least 4GB RAM (Memory) to the Docker engine, otherwise the build will fail.
5. Run `docker-compose build`.
6. Run `docker-compose up -d` and enjoy!
## via Command Line:
1. Clone the repo: `git clone https://scm.cms.hu-berlin.de/callidus/mc_frontend.git`
2. Move to the newly created folder: `cd mc_frontend`
3. Run `npm install`
4. Run `npm install -g @angular/cli` (you may need `sudo`).
5. Check that the Angular command line interface is installed by running `ng --version`. It should print the version of the Angular CLI.
6. Run `npm start`.
If you already ran `npm install` and the CLI still complains about missing dependencies, install them one by one using `npm install DEPENDENCY_NAME`. 
7. Open http://localhost:8100 in your browser.
## Production Build
To build the application for production environments, use: `ionic cordova build browser --prod --release --max-old-space-size=4096` and serve the content of the `platforms/browser/www` folder, e.g. with Nginx.
# Development
To add new pages to the application, use: `ionic generate page PAGE_NAME`.
# Access to the Docker container
Use `docker-compose down` to stop and remove the currently running containers.
To access a running container directly, get the container ID via `docker ps` and connect via `docker exec -it CONTAINER_ID bash`. Or, for root access, use: `docker exec -u 0 -it CONTAINER_ID bash`
To snapshot a running container, use `docker commit CONTAINER_ID`. It returns a snapshot ID, which you can access via `docker run -it SNAPSHOT_ID`.
# Configuration
## Backend URL
To change the URL for the backend, use the `ionic.config.json` file (proxies > proxyUrl). By default, the system assumes that backend and frontend are installed on the same machine.
## Frontend URL
Use the `--host 0.0.0.0 --disable-host-check` flag for `ng serve` if you want to use it in a production environment with an Nginx server using proxy_pass.
## Other
For all other kinds of configuration, use `src/configMC.ts`.
# Testing
To test the application and check the code coverage, run `npm run test`.
To write new tests or debug existing ones, use `npm run test-debug`.
