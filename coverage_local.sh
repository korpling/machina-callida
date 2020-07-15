docker-compose build
docker-compose run --rm --entrypoint="npm run test-ci" mc_frontend >ci_frontend.log
docker-compose run --rm --entrypoint="./coverage_backend.sh" mcserver > ci_backend.log
./coverage_ci.sh
cat coverage.log
