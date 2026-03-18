local Greeter = {}
Greeter.__index = Greeter

function Greeter.new(name)
    local self = setmetatable({}, Greeter)
    self.name = name
    return self
end

function Greeter:greet()
    return "Hello, " .. self.name .. "!"
end

local g = Greeter.new("World")
print(g:greet())
