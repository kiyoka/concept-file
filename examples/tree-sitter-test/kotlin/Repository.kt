package com.example.data

data class Entity(val id: Long, val name: String, val active: Boolean)

interface Repository<T> {
    fun findById(id: Long): T?
    fun findAll(): List<T>
    fun save(entity: T): T
    fun delete(id: Long): Boolean
}

class InMemoryRepository : Repository<Entity> {
    private val store = mutableMapOf<Long, Entity>()
    private var nextId = 1L

    override fun findById(id: Long): Entity? {
        return store[id]
    }

    override fun findAll(): List<Entity> {
        return store.values.toList()
    }

    override fun save(entity: Entity): Entity {
        val saved = entity.copy(id = nextId++)
        store[saved.id] = saved
        return saved
    }

    override fun delete(id: Long): Boolean {
        return store.remove(id) != null
    }

    fun findByName(name: String): List<Entity> {
        return store.values.filter { it.name == name }
    }

    fun count(): Int = store.size
}

fun main() {
    val repo = InMemoryRepository()
    repo.save(Entity(0, "Alice", true))
    repo.save(Entity(0, "Bob", false))
    println(repo.findAll())
}
