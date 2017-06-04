FROM base/archlinux:latest
MAINTAINER guni973

RUN pacman -Syyu  --noconfirm
RUN pacman-db-upgrade
RUN pacman -S     --noconfirm base base-devel && \
    pacman -S     --noconfirm python python-pip git cmake gcc boost

RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN git clone https://github.com/marron-general/TPTS_web /usr/src/TPTS_web

WORKDIR /usr/src/TPTS_web/
ADD setting.json /usr/src/TPTS_web
RUN python -m venv venv
RUN source venv/bin/activate
RUN pip install -r requirements.txt
RUN pip install dlib

CMD git pull
CMD python adminTL.py & python main.py

