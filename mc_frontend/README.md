# Installing the frontend via command line
1. Clone the repo: `git clone https://scm.cms.hu-berlin.de/callidus/machina-callida.git`
2. Move to the newly created folder: `cd machina-callida/mc_frontend`
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
# Configuration
## Backend URL
To change the URL for the backend, use the `ionic.config.json` file (proxies > proxyUrl). By default, the system assumes that backend and frontend are installed on the same machine.
## Frontend URL
Use the `--host 0.0.0.0 --disable-host-check` flag for `ng serve` if you want to use it in a production environment with an Nginx server using proxy_pass.
## Other
For all other kinds of configuration, use `src/configMC.ts`.
# Testing
To test the application and check the code coverage, run `npm run test-ci`.
To write new tests or debug existing ones, use `npm run test-debug`.
