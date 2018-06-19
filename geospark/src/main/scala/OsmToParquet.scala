import org.apache.log4j.{Level, Logger}
import org.apache.spark.serializer.KryoSerializer
import org.apache.spark.sql.SparkSession
import org.datasyslab.geospark.serde.GeoSparkKryoRegistrator
import org.datasyslab.geosparksql.utils.GeoSparkSQLRegistrator

object OsmToParquet extends App {
  Logger.getLogger("org").setLevel(Level.WARN)
  Logger.getLogger("akka").setLevel(Level.WARN)

  var sparkSession:SparkSession = SparkSession.builder()
    .config("spark.serializer", classOf[KryoSerializer].getName)
    .config("spark.kryo.registrator", classOf[GeoSparkKryoRegistrator].getName)
    .master("local[*]")
    .appName("Generate Parquet").getOrCreate()

  GeoSparkSQLRegistrator.registerAll(sparkSession)

  val opts = Map(
    "url" -> "jdbc:postgresql://localhost:54320/gis",
    "user" -> "postgres",
    "driver" -> "org.postgresql.Driver")

  writePostgresToParquet()

  def writePostgresToParquet() = {
    sparkSession.read.format("jdbc").options(opts).option("dbtable", "planet_osm_point").load.createOrReplaceTempView("points")
    sparkSession.read.format("jdbc").options(opts).option("dbtable", "planet_osm_polygon").load.createOrReplaceTempView("polygons")

    sparkSession.sql("SELECT osm_id, way AS geometry, amenity, leisure, landuse, shop, access FROM points").write.parquet("out/points.parquet")
    sparkSession.sql("SELECT osm_id, way AS geometry, amenity, leisure, landuse, shop, access FROM polygons").write.parquet("out/polygons.parquet")
  }
}
