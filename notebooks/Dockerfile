FROM jupyter/base-notebook:latest

RUN conda install --yes --no-pin \
      geopandas \
      folium \
      osmnx=0.7.0 \
      gmaps

USER root

EXPOSE 8888
