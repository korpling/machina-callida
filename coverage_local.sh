docker-compose build
docker-compose run --rm --entrypoint="npm run test-ci" mc_frontend > ci_frontend.log
docker-compose run --rm mcserver bash -c "source ../venv/bin/activate && coverage run --rcfile=.coveragerc tests.py && coverage combine && coverage report -m" > ci_backend.log
./coverage_ci.sh
cat coverage.log
