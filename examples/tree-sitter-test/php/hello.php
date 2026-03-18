<?php

class Greeter {
    private string $name;

    public function __construct(string $name) {
        $this->name = $name;
    }

    public function greet(): string {
        return "Hello, {$this->name}!";
    }
}

$g = new Greeter("World");
echo $g->greet() . "\n";
