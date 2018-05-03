DROP TABLE IF EXISTS clusters;
CREATE TABLE clusters (
  id SERIAL,
  hull geometry,
  area integer,
  pois_count integer,
  dbscan_minPts integer
);

INSERT INTO clusters(hull, area, pois_count) (
  WITH clustered_pois AS (
    SELECT geometry, ST_ClusterDBSCAN(geometry, 100, 3) over () as cid FROM pois
  )
  SELECT ST_ConcaveHull(ST_Union(geometry), 0.9),
         ST_Area(ST_ConvexHull(ST_Union(geometry))),
         COUNT(geometry)
  FROM clustered_pois AS hull WHERE cid > 0 GROUP BY cid
);

UPDATE clusters SET dbscan_minPts = GREATEST(2, round((-5.342775355 * 10^(-7) * area + 5.738819175 * 10^(-3) * pois_count + 2.912834423)));

CREATE INDEX clusters_hull ON clusters USING gist(hull);
