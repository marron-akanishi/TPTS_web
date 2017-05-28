# FROM archlinuxjp/docker-arch
FROM base/archlinux
# RUN docker-arch -l yaourt

# MAINTAINER guni973

RUN pacman -Syyu  --noconfirm
RUN pacman-db-upgrade
RUN pacman -S     --noconfirm base base-devel && \
    pacman -S     --noconfirm python python-pip git cmake gcc boost


RUN git clone https://github.com/marron-akanishi/TPTS_web /usr/src/TPTS_web
WORKDIR /usr/src/TPTS_web/
RUN git pull

ADD collect/oauth.py /usr/src/TPTS_web/collect
RUN python -m venv venv
RUN source venv/bin/activate
RUN pip install -r requirements.txt
RUN pip install dlib

CMD python collect/TL.py & python main.py 

