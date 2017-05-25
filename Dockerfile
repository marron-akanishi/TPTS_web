FROM archlinuxjp/docker-arch
RUN docker-arch -l yaourt
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm python python-pip git

RUN git clone https://github.com/guni973/TPTS_web
WORKDIR /usr/src/TPTS_web/

ADD oauth.py /usr/src/TPTS_web/
RUN yaourt -S python-glib
RUN python -m venv venv
RUN source venv/bin/activate
RUN pip install -r requirements.txt

CMD python main runserver

