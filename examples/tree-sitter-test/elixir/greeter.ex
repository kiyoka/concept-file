defmodule Greeter do
  def hello(name) do
    "Hello, #{name}!"
  end

  def main do
    IO.puts(hello("World"))
  end
end
