FROM jupyter/base-notebook:latest

RUN conda install --yes --no-pin \
      geopandas \
      folium

USER root

RUN sudo apt-get update && sudo apt-get install osm2pgsql

EXPOSE 8888
