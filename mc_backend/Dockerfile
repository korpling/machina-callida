#do not use an alpine-based image, it is too cumbersome to install all the necessary components to make the C/C++
#dependencies in the requirements.txt work
FROM python:3.8

RUN useradd -ms /bin/bash mc
WORKDIR /home/mc
RUN python -m venv venv
COPY requirements.txt requirements.txt
RUN venv/bin/pip install --no-cache-dir --default-timeout=120 -r requirements.txt
COPY . mc_backend
WORKDIR /home/mc/mc_backend
