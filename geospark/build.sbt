import sbt.Keys.{libraryDependencies, mainClass, version}


lazy val root = (project in file(".")).
  settings(
    name := "OsmAOI",

    version := "0.1.0",

    scalaVersion := "2.11.8",

    mainClass in assembly := Some("QueryOsmAOI")
  )

val SparkVersion = "2.3.0"

val SparkCompatibleVersion = "2.3"

val HadoopVersion = "2.7.2"

val GeoSparkVersion = "1.1.3"

val dependencyScope = "compile"

logLevel := Level.Warn

logLevel in assembly := Level.Error

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % SparkVersion % dependencyScope,
  "org.apache.spark" %% "spark-sql" % SparkVersion % dependencyScope,
  "org.datasyslab" % "geospark" % GeoSparkVersion,
  "org.datasyslab" % "geospark-sql_".concat(SparkCompatibleVersion) % GeoSparkVersion,
  "org.postgresql" % "postgresql" % "42.1.1" % dependencyScope,
  "org.alitouka" % "spark_dbscan_2.10" % "0.0.5"
)

assemblyMergeStrategy in assembly := {
  case PathList("org.datasyslab", "geospark", xs@_*) => MergeStrategy.first
  case PathList("META-INF", "MANIFEST.MF") => MergeStrategy.discard
  case path if path.endsWith(".SF") => MergeStrategy.discard
  case path if path.endsWith(".DSA") => MergeStrategy.discard
  case path if path.endsWith(".RSA") => MergeStrategy.discard
  case _ => MergeStrategy.first
}

resolvers +=
  "Sonatype OSS Snapshots" at "https://oss.sonatype.org/content/repositories/snapshots"

resolvers +=
  "Open Source Geospatial Foundation Repository" at "http://download.osgeo.org/webdav/geotools"

resolvers += "Aliaksei Litouka's repository" at "http://alitouka-public.s3-website-us-east-1.amazonaws.com/"