class Greeter
  attr_reader :name

  def initialize(name)
    @name = name
  end

  def greet
    "Hello, #{name}!"
  end
end

puts Greeter.new("World").greet
