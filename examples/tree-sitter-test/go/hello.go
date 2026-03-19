package main

import "fmt"

type Greeter struct {
	Name string
}

func (g Greeter) Greet() string {
	return fmt.Sprintf("Hello, %s!", g.Name)
}

func main() {
	g := Greeter{Name: "World"}
	fmt.Println(g.Greet())
}
