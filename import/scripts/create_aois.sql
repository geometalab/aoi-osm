DROP TABLE IF EXISTS aois;

CREATE TABLE aois(hull geometry);

INSERT INTO aois (
  WITH clusters AS (
    SELECT * FROM clusters
  ),
  point_clusters_per_cluster AS (
    SELECT clusters.id AS cluster_id,
           geometry,
           ST_ClusterDBSCAN(geometry, eps := 35, minpoints := clusters.dbscan_minpts) over () AS cid
    FROM pois, clusters
    WHERE ST_Within(geometry, clusters.hull)
  )
  SELECT ST_ConcaveHull(ST_Union(geometry), 0.99) AS geometry FROM point_clusters_per_cluster WHERE cid IS NOT NULL GROUP BY cluster_id, cid
)
