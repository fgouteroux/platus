FROM python:2.7

RUN useradd --user-group --create-home --shell /bin/false platus

ENV INSTALL_PATH /platus
RUN mkdir -p $INSTALL_PATH && chown platus:platus /platus

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

USER platus

COPY . .

CMD gunicorn -b 0.0.0.0:5001 main:application