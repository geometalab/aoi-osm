import org.apache.commons.math3.ml.clustering.Clusterable

class OwnPoint(x: Double, y: Double) extends Clusterable {
  override def getPoint: Array[Double] = {
    return Array(x, y)
  }
}
