docker-compose run --rm mcserver bash -c "source ../venv/bin/activate && coverage run --rcfile=.coveragerc tests.py && coverage combine && coverage report -m" > ci_backend.log
