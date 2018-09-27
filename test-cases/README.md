The [manual_aois](manual_aois/) directory contains the manually drawn AOIs. These AOIs are 
used as a benchmark for evaluating the optimal eps and minpoints arguments for 
the DBSCAN algorithm. 

List of AOI test cases:

* **Geoname; Author; Coordinates (lat,lon); visual examplification**
* Rapperswil (CH); Stefan; 47.22692,8.82361;
* Zürich City (CH); Stefan; ???
* Stäfa (CH); Stefan; ???
* Witikon (CH); 47.3582/8.5885 http://umap.openstreetmap.fr/en/map/manual_aoi_witikon_ch_249276#16/47.3582/8.5885
* Halle (BE); Joost; 50.73601,4.23786; http://umap.openstreetmap.fr/nl/map/manual-aoi-halle_239532#16/50.7361/4.2362
* Singapore (SG); 1.3466/103.8210 http://umap.openstreetmap.fr/en/map/manual_aoi_singapore_sg_249279#12/1.3466/103.8210
* UBS IT Altstetten/Zürich; Jerry; ???
* English East Midlands; Jerry; ???
* Germany; Jerry; ???
* ...

Note: These test cases are used to evaluate and optimize the AOI algorithm by visually comparing but also using automated comparisons (e.g. percentage of area overlap). 
