#do not use an alpine-based image, it is too cumbersome to install all the necessary components to make the C/C++
#dependencies in the requirements.txt work
FROM python:3.8

RUN useradd -ms /bin/bash mc

WORKDIR /home/mc

RUN python -m venv venv

RUN apt-get update
RUN apt-get install -y openssh-server nano

COPY mcserver/requirements.txt requirements.txt
RUN venv/bin/pip install --no-cache-dir --default-timeout=120 -r requirements.txt

#prepare ssh
RUN mkdir /var/run/sshd
RUN echo 'root:root' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
RUN /usr/bin/ssh-keygen -A
CMD ["/usr/sbin/sshd", "-D"]

COPY . mc_backend

WORKDIR /home/mc/mc_backend
