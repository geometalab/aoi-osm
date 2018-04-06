FROM python:3

ADD . /webapp
WORKDIR /webapp

RUN pip install -r requirements.txt

ENV FLASK_APP="webapp.py"
ENV FLASK_DEBUG=True

EXPOSE 5000

CMD ["/bin/sh", "-l", "-c", "flask run --host 0.0.0.0"]
