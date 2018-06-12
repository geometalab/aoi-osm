FROM python:3

RUN wget http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz
RUN tar -xvf spatialindex-src-1.8.5.tar.gz
RUN cd spatialindex-src-1.8.5 && ./configure; make; make install; ldconfig

ADD . /webapp
WORKDIR /webapp

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install --yes osm2pgsql gdal-bin postgresql-client-9.4

ENV FLASK_APP="webapp.py"
ENV FLASK_DEBUG=True

EXPOSE 5000

CMD ["/bin/sh", "-l", "-c", "flask run --host 0.0.0.0"]
