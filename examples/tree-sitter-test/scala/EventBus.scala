package com.example.events

import scala.collection.mutable

trait Event {
  def name: String
  def timestamp: Long
}

case class UserEvent(name: String, userId: String, timestamp: Long) extends Event

case class SystemEvent(name: String, level: String, timestamp: Long) extends Event

trait EventHandler[E <: Event] {
  def handle(event: E): Unit
}

class EventBus {
  private val handlers: mutable.Map[String, List[EventHandler[_ <: Event]]] = mutable.Map.empty

  def subscribe[E <: Event](eventName: String, handler: EventHandler[E]): Unit = {
    val existing = handlers.getOrElse(eventName, List.empty)
    handlers(eventName) = existing :+ handler
  }

  def publish(event: Event): Unit = {
    handlers.getOrElse(event.name, List.empty).foreach { handler =>
      handler.asInstanceOf[EventHandler[Event]].handle(event)
    }
  }

  def unsubscribeAll(eventName: String): Unit = {
    handlers.remove(eventName)
  }

  val subscriberCount: Int = handlers.values.map(_.size).sum
}

object EventBus {
  def apply(): EventBus = new EventBus()
}
