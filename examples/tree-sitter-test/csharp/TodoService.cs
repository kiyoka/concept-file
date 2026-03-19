using System;
using System.Collections.Generic;
using System.Linq;

namespace TodoApp
{
    public enum Priority
    {
        Low,
        Medium,
        High
    }

    public class TodoItem
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public bool IsComplete { get; set; }
        public Priority Priority { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    public interface ITodoService
    {
        TodoItem Add(string title, Priority priority);
        void Complete(int id);
        void Delete(int id);
        List<TodoItem> GetAll();
        List<TodoItem> GetPending();
    }

    public class TodoService : ITodoService
    {
        private readonly List<TodoItem> _items = new();
        private int _nextId = 1;

        public TodoItem Add(string title, Priority priority)
        {
            var item = new TodoItem
            {
                Id = _nextId++,
                Title = title,
                Priority = priority,
                CreatedAt = DateTime.UtcNow
            };
            _items.Add(item);
            return item;
        }

        public void Complete(int id)
        {
            var item = _items.FirstOrDefault(i => i.Id == id);
            if (item != null) item.IsComplete = true;
        }

        public void Delete(int id)
        {
            _items.RemoveAll(i => i.Id == id);
        }

        public List<TodoItem> GetAll()
        {
            return _items.OrderBy(i => i.Priority).ToList();
        }

        public List<TodoItem> GetPending()
        {
            return _items.Where(i => !i.IsComplete).ToList();
        }
    }
}
