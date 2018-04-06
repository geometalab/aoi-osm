FROM jupyter/base-notebook:latest

RUN conda install --yes --no-pin \
      geopandas \
      folium \
      osmnx=0.7.0

USER root

RUN sudo apt-get update && sudo apt-get install --yes osm2pgsql

EXPOSE 8888
