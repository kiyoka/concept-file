struct Greeter {
    let name: String

    func greet() -> String {
        return "Hello, \(name)!"
    }
}

let greeter = Greeter(name: "World")
print(greeter.greet())
