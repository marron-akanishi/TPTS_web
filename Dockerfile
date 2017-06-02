FROM base/archlinux

MAINTAINER guni973

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN pacman -Syyu  --noconfirm
RUN pacman-db-upgrade
RUN pacman -S     --noconfirm base base-devel && \
    pacman -S     --noconfirm python python-pip git cmake gcc boost

RUN git clone https://github.com/guni973/TPTS_web /usr/src/TPTS_web

WORKDIR /usr/src/TPTS_web/
ADD collect/oauth.py /usr/src/TPTS_web/collect
RUN python -m venv venv
RUN source venv/bin/activate
RUN pip install -r requirements.txt
RUN pip install dlib

CMD git pull
CMD python collect/TL.py & python main.py

