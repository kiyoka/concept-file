case class Greeter(name: String) {
  def greet: String = s"Hello, $name!"
}

object Main extends App {
  val greeter = Greeter("World")
  println(greeter.greet)
}
