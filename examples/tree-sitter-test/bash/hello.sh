#!/bin/bash

greet() {
    local name="$1"
    echo "Hello, ${name}!"
}

add() {
    echo $(( $1 + $2 ))
}

greet "World"
add 3 4
