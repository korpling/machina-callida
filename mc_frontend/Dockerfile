FROM node:10.19.0-stretch

RUN useradd -ms /bin/bash mc

WORKDIR /home/mc
RUN apt update
# for testing with headless chrome browser
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install -y ./google-chrome-stable_current_amd64.deb

WORKDIR /home/mc/mc_frontend
COPY package.json .
# to get the version of the local CLI package, run: npm list @angular/cli | sed 's/[^0-9.]*//g' | sed -n 2p
RUN npm i -g @angular/cli
# this makes the analytics prompt during upcoming "npm install" disappear, so this can also run in CI
RUN ng analytics off
RUN npm install

COPY . .
COPY ./config.xml ./www/config.xml

# workaround to fix the missing binding issue for node-sass
RUN npm rebuild node-sass
