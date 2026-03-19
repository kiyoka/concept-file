local Entity = {}
Entity.__index = Entity

function Entity.new(name, x, y)
    local self = setmetatable({}, Entity)
    self.name = name
    self.x = x
    self.y = y
    self.health = 100
    return self
end

function Entity:move(dx, dy)
    self.x = self.x + dx
    self.y = self.y + dy
end

function Entity:damage(amount)
    self.health = math.max(0, self.health - amount)
end

function Entity:isAlive()
    return self.health > 0
end

local World = {}
World.__index = World

function World.new(width, height)
    local self = setmetatable({}, World)
    self.width = width
    self.height = height
    self.entities = {}
    return self
end

function World:addEntity(entity)
    table.insert(self.entities, entity)
end

function World:update(dt)
    for _, entity in ipairs(self.entities) do
        if entity.isAlive and entity:isAlive() then
            -- update logic
        end
    end
end

function World:findNearby(x, y, radius)
    local found = {}
    for _, entity in ipairs(self.entities) do
        local dx = entity.x - x
        local dy = entity.y - y
        if math.sqrt(dx*dx + dy*dy) <= radius then
            table.insert(found, entity)
        end
    end
    return found
end

return {
    Entity = Entity,
    World = World,
}
