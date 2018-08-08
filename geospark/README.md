## Apache Spark Implementation

This is the Apache Spark implementation to generate AOIs from OpenStreetMap
data. The goal is to evaluate how much functionality of the [PostgreSQL
implementation](https://github.com/philippks/ma-osm-aoi/tree/master/webapp) can
be implemented with Apache Spark.

To get started, open this project with [Intellij](https://www.jetbrains.com/idea/).

First the OpenStreetMap data needs to be converted to Parquet files. To do that,
open `OsmToParquet.scala` file and point the database configuration to a PostgreSQL
database with an import of `osm2pgsql`. When executing, two Parquet files
`points.parquet` and `polygons.parquet` gets created.

Afterwards, the file `GenerateAois.scala` can be executed, what generates the
`aois.geojson`.
