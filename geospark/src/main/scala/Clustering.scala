import com.vividsolutions.jts.geom.Geometry
import org.alitouka.spark.dbscan.{Dbscan, DbscanSettings, RawDataSet}
import org.alitouka.spark.dbscan.spatial.Point
import org.alitouka.spark.dbscan.DistributedDbscan
import org.alitouka.spark.dbscan.spatial.rdd.PartitioningSettings
import org.apache.log4j.{Level, Logger}
import org.apache.spark.api.java.JavaPairRDD
import org.apache.spark.rdd.RDD
import org.apache.spark.serializer.KryoSerializer
import org.apache.spark.sql.{Row, SparkSession}
import org.apache.spark.sql.types.{LongType, StringType, StructField, StructType}
import org.datasyslab.geospark.enums.GridType
import org.datasyslab.geospark.serde.GeoSparkKryoRegistrator
import org.datasyslab.geospark.spatialOperator.JoinQuery
import org.datasyslab.geospark.spatialRDD.SpatialRDD
import org.datasyslab.geosparksql.utils.{Adapter, GeoSparkSQLRegistrator}

import scala.reflect.io.Path
import scala.util.Try

object Clustering extends App {
  Logger.getLogger("org").setLevel(Level.WARN)
  Logger.getLogger("akka").setLevel(Level.WARN)

  var sparkSession:SparkSession = SparkSession.builder()
    .config("spark.serializer", classOf[KryoSerializer].getName)
    .config("spark.kryo.registrator", classOf[GeoSparkKryoRegistrator].getName)
    .master("local[*]")
    .appName("Generate Parquet").getOrCreate()

  GeoSparkSQLRegistrator.registerAll(sparkSession)


  dbscanClustering()

  def toCSVLine(point:Point):String = {
    return point.coordinates(0) + "," + point.coordinates(1) + "," + point.clusterId
  }

  def dbscanClustering() = {
    sparkSession.read.parquet("out/points.parquet").createOrReplaceTempView("points")
    sparkSession.read.parquet("out/polygons.parquet").createOrReplaceTempView("polygons")

    val tagConditions = Settings.tags.map { case (key, values) => "array_contains(array("+values.map { value => "'" + value + "'"} .mkString(",")+"), "+key+")" }.toList
    val tagConditionsQuery = tagConditions.mkString(" OR ")

/*
    val poisDataFrame = sparkSession.sql(
      """
        |SELECT id, ST_Transform(ST_GeomFromWKB(geometry), 'epsg:3857','epsg:4326')
        |FROM points
        |WHERE access IS DISTINCT FROM 'private' AND (""".stripMargin + tagConditionsQuery +
      """ ) LIMIT 1000
        | UNION
        | SELECT 1000000000 + id AS id, ST_Centroid(ST_Transform(ST_GeomFromWKB(geometry), 'epsg:3857','epsg:4326'))
        | FROM polygons
        | WHERE access IS DISTINCT FROM 'private' AND (""".stripMargin + tagConditionsQuery + """
        | ) LIMIT 1000
      """.stripMargin
      */
    val poisDataFrame = sparkSession.sql("""
    |SELECT osm_id, ST_Transform(ST_GeomFromWKB(geometry), 'epsg:3857','epsg:4326')
    |FROM points
    |WHERE access IS DISTINCT FROM 'private' AND (""".stripMargin + tagConditionsQuery +
    """ ) LIMIT 1000""".stripMargin)

    poisDataFrame.show(10)

    val poisPoints = poisDataFrame.rdd.map(row => new Point(row.getAs[Geometry](1).getCoordinates()(0).y, row.getAs[Geometry](1).getCoordinates()(0).x).withPointId(row.getAs[Long](0)))

    poisPoints.take(10).foreach(println)
    val count = poisPoints.count()
    println("total number of points: " + count)

    val clusteringSettings = new DbscanSettings().withEpsilon(0.0009).withNumberOfPoints(3)
    //val partitionSettings = new PartitioningSettings(numberOfPointsInBox = count / 4)
    val model = Dbscan.train(poisPoints, clusteringSettings)

    //Try(Path("out/preclustered_pois.csv").deleteRecursively())
    //model.clusteredPoints.map(toCSVLine).saveAsTextFile("out/preclustered_pois.csv")

    val preclusteredPois = model.clusteredPoints.map { point => Row(point.pointId, point.clusterId)}
    preclusteredPois.take(10).foreach(println)

    val schema = new StructType(Array(StructField("osm_id",LongType),StructField("clusterId",LongType)))
    sparkSession.createDataFrame(preclusteredPois, schema).createOrReplaceTempView("preclustered_pois")

    sparkSession.sql("SELECT * FROM preclustered_pois").show()
  }
}
