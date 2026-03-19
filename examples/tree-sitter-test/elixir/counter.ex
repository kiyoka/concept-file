defmodule Counter do
  use GenServer

  def start_link(initial_value \\ 0) do
    GenServer.start_link(__MODULE__, initial_value, name: __MODULE__)
  end

  def increment do
    GenServer.call(__MODULE__, :increment)
  end

  def decrement do
    GenServer.call(__MODULE__, :decrement)
  end

  def value do
    GenServer.call(__MODULE__, :value)
  end

  def reset do
    GenServer.cast(__MODULE__, :reset)
  end

  # Server callbacks

  def init(initial_value) do
    {:ok, initial_value}
  end

  def handle_call(:increment, _from, state) do
    {:reply, state + 1, state + 1}
  end

  def handle_call(:decrement, _from, state) do
    {:reply, state - 1, state - 1}
  end

  def handle_call(:value, _from, state) do
    {:reply, state, state}
  end

  def handle_cast(:reset, _state) do
    {:noreply, 0}
  end
end
