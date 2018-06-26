import com.vividsolutions.jts.geom.Geometry
import org.alitouka.spark.dbscan.spatial.Point
import org.alitouka.spark.dbscan.{Dbscan, DbscanSettings}
import org.apache.commons.math3.ml.clustering.{Cluster, DBSCANClusterer}
import org.apache.log4j.{Level, Logger}
import org.apache.spark.serializer.KryoSerializer
import org.apache.spark.sql.types._
import org.apache.spark.sql.{Row, SparkSession}
import org.datasyslab.geospark.serde.GeoSparkKryoRegistrator
import org.datasyslab.geospark.spatialRDD.SpatialRDD
import org.datasyslab.geosparksql.utils.{Adapter, GeoSparkSQLRegistrator}

import scala.collection.JavaConverters._
import scala.sys.process._

object GenerateAois extends App {
  Logger.getLogger("org").setLevel(Level.WARN)
  Logger.getLogger("akka").setLevel(Level.WARN)

  var sparkSession:SparkSession = SparkSession.builder()
    .config("spark.serializer", classOf[KryoSerializer].getName)
    .config("spark.kryo.registrator", classOf[GeoSparkKryoRegistrator].getName)
    //.master("local[*]")
    .appName("Generate Parquet").getOrCreate()

  GeoSparkSQLRegistrator.registerAll(sparkSession)

  dbscanClustering()
/*
  def toCSVLine(aoi:(Double, Double, Integer)):String = {
    return point.coordinates(0) + "," + point.coordinates(1) + "," + point.clusterId
  }
*/
  def dbscanClustering() = {
    print("enter num partitions:")
    val num_partitions = scala.io.StdIn.readLine().toInt

    val t0 = System.nanoTime()

    sparkSession.read.parquet("/data/out/points.parquet").createOrReplaceTempView("points")
    sparkSession.read.parquet("/data/out/polygons.parquet").createOrReplaceTempView("polygons")

    val tagConditions = Settings.tags.map { case (key, values) => "array_contains(array("+values.map { value => "'" + value + "'"} .mkString(",")+"), "+key+")" }.toList
    val tagConditionsQuery = tagConditions.mkString(" OR ")

    val poisDataFrame = sparkSession.sql(
      """
        |SELECT osm_id, ST_Transform(ST_GeomFromWKB(geometry), 'epsg:3857','epsg:4326')
        |FROM points
        |WHERE access IS DISTINCT FROM 'private' AND (""".stripMargin + tagConditionsQuery +
      """ )
        | UNION
        | SELECT osm_id, ST_Centroid(ST_Transform(ST_GeomFromWKB(geometry), 'epsg:3857','epsg:4326'))
        | FROM polygons
        | WHERE access IS DISTINCT FROM 'private' AND (""".stripMargin + tagConditionsQuery + """
        | )
      """.stripMargin)
    /*
    val poisDataFrame = sparkSession.sql("""
    |SELECT osm_id, ST_Transform(ST_GeomFromWKB(geometry), 'epsg:3857','epsg:4326')
    |FROM points
    |WHERE access IS DISTINCT FROM 'private' AND (""".stripMargin + tagConditionsQuery +
    """ ) LIMIT 1000""".stripMargin)
    */

    poisDataFrame.repartition(num_partitions)


    println("relevant pois (count:" + poisDataFrame.count() + "): ")
    poisDataFrame.show(10)

    println("convert pois to points for DBSCAN:")
    val poisPoints = poisDataFrame.rdd.map(row => new Point(row.getAs[Geometry](1).getCoordinates()(0).y, row.getAs[Geometry](1).getCoordinates()(0).x))
    poisPoints.take(10).foreach(println)

    val clusteringSettings = new DbscanSettings().withEpsilon(0.0009).withNumberOfPoints(3)
    //val partitionSettings = new PartitioningSettings(numberOfPointsInBox = count / 4)
    val model = Dbscan.train(poisPoints, clusteringSettings)

    println("pois preclustered with DBSCAN:")
    val preclusteredPois = model.clusteredPoints.map { point => Row(point.coordinates(0), point.coordinates(1), point.clusterId)}
    println("total pre-clusters: " + preclusteredPois.count())
    preclusteredPois.take(10).foreach(println)


    println("calculate areas of pre-clusters...")
    val schema = new StructType(Array(StructField("x",DoubleType),StructField("y",DoubleType),StructField("cluster_id",LongType)))
    sparkSession.createDataFrame(preclusteredPois, schema).createOrReplaceTempView("preclustered_pois")

    sparkSession.sql("SELECT ST_Point(CAST(x AS Decimal(24,20)),CAST(y AS Decimal(24,20))) AS geometry, cluster_id FROM preclustered_pois").createOrReplaceTempView("preclustered_pois")
    sparkSession.sql(
      """SELECT cluster_id, ST_ConvexHull(ST_Envelope_Aggr(geometry)) AS hull,
        |ST_Area(ST_ConvexHull(ST_Envelope_Aggr(geometry))) AS area,
        |COUNT(geometry) AS pois_count
        |FROM preclustered_pois
        |GROUP BY cluster_id""".stripMargin).createOrReplaceTempView("preclusters")

    sparkSession.sql(
      """SELECT cluster_id,
        |GREATEST(2, round((-5.342775355 * 0.0000001 * area + 5.738819175 * 0.001 * pois_count + 2.912834423))) AS dbscan_minPts
        |FROM preclusters""".stripMargin).createOrReplaceTempView("preclusters")

    println("and calculate minPts for DBSCAN...")
    val preclusteredPoisWithMinPts = sparkSession.sql(
      """SELECT preclustered_pois.cluster_id AS cluster_id, dbscan_minPts, geometry
        |FROM preclustered_pois, preclusters
        |WHERE preclusters.cluster_id = preclustered_pois.cluster_id AND preclustered_pois.cluster_id > 0""".stripMargin).rdd
    preclusteredPoisWithMinPts.take(10).foreach(println)

    preclusteredPoisWithMinPts.count()
    println("Pre-Clustering time: " + (System.nanoTime() - t0) / 1000 / 1000 / 1000 + "s")

    println("calculate DBSCAN for each pre-cluster")
    val aois = preclusteredPoisWithMinPts.groupBy(poi => poi.getLong(0)).map {
      case (cluster_id, pois) => {
        val minPts = pois.last.getDouble(1).asInstanceOf[Int]
        val eps = 0.0004

        val points = pois.map(row => new OwnPoint(row.getAs[com.vividsolutions.jts.geom.Point](2).getCoordinates()(0).y, row.getAs[com.vividsolutions.jts.geom.Point](2).getCoordinates()(0).x) )
        val clusterer = new DBSCANClusterer[OwnPoint](eps, minPts)

        println("   cluster points: " + points.size)
        val clusters = clusterer.cluster(points.asJavaCollection)
        println("   resulting clusters: " + clusters.size())

        clusters.toArray().map(cluster => (cluster_id << 3 + clusters.indexOf(cluster), cluster.asInstanceOf[Cluster[OwnPoint]].getPoints.toArray().map(point => point.asInstanceOf[OwnPoint].getPoint)))
      }
    }.reduce(_++_)
      .map { case (cluster_id, points) => points.map(point => (point(0), point(1), cluster_id)) }
      .reduce(_++_)
      .map { clustered_poi => Row(clustered_poi._1, clustered_poi._2, clustered_poi._3)}

    val clustered_pois_schema = new StructType(Array(StructField("x",DoubleType),StructField("y",DoubleType),StructField("cluster_id",LongType)))
    sparkSession.createDataFrame(sparkSession.sparkContext.parallelize(aois), clustered_pois_schema).createOrReplaceTempView("clustered_pois")

    sparkSession.sql("SELECT ST_Point(CAST(x AS Decimal(24,20)),CAST(y AS Decimal(24,20))) AS geometry, cluster_id FROM clustered_pois").createOrReplaceTempView("clustered_pois")
    val aoisDataFrame = sparkSession.sql("SELECT ST_ConvexHull(ST_Envelope_Aggr(geometry)) AS aoi FROM clustered_pois GROUP BY cluster_id")

    println("final aois count: " + aoisDataFrame .count())
    println("Clustering time: " + (System.nanoTime() - t0) / 1000 / 1000 / 1000 + "s")


    val spatialAoisRDD = new SpatialRDD[Geometry]
    spatialAoisRDD.rawSpatialRDD = Adapter.toRdd(aoisDataFrame)
    "rm -R /data/out/aois.export" !;
    spatialAoisRDD.saveAsGeoJSON("/data/out/aois.export")

    "cat /data/out/aois.export/* | sed '$!s/$/,/' > /data/out/aois.geojson" !

    println("Export time: " + (System.nanoTime() - t0) / 1000 / 1000 / 1000 + "s")

    scala.io.StdIn.readLine()
  }
}
