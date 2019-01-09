DROP TABLE IF EXISTS preclusters;
CREATE TABLE preclusters (
  id SERIAL,
  hull geometry,
  area integer,
  pois_count integer,
  dbscan_minPts integer
);

SELECT UpdateGeometrySRID('preclusters', 'hull', 3857);

INSERT INTO preclusters(hull, area, pois_count) (
  WITH clustered_pois AS (
    SELECT geometry, ST_ClusterDBSCAN(geometry, 100, 3) over () as cid FROM pois
  )
  SELECT ST_ConvexHull(ST_Union(geometry)),
         ST_Area(ST_ConvexHull(ST_Union(geometry))),
         COUNT(geometry)
  FROM clustered_pois AS hull WHERE cid >= 0 GROUP BY cid
);

UPDATE preclusters SET dbscan_minPts = GREATEST(2, round((-5.342775355 * 10^(-7) * area + 5.738819175 * 10^(-3) * pois_count + 2.912834423)));

CREATE INDEX preclusters_hull ON preclusters USING gist(hull);
