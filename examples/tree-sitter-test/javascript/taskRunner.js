import { EventEmitter } from 'events';

export class Task {
  constructor(name, fn) {
    this.name = name;
    this.fn = fn;
    this.status = 'pending';
  }

  async run() {
    this.status = 'running';
    try {
      const result = await this.fn();
      this.status = 'done';
      return result;
    } catch (err) {
      this.status = 'failed';
      throw err;
    }
  }
}

export class TaskRunner extends EventEmitter {
  constructor(concurrency = 4) {
    super();
    this.concurrency = concurrency;
    this.queue = [];
    this.running = 0;
  }

  add(task) {
    this.queue.push(task);
    this.emit('added', task);
  }

  async runAll() {
    const results = [];
    while (this.queue.length > 0 || this.running > 0) {
      while (this.running < this.concurrency && this.queue.length > 0) {
        const task = this.queue.shift();
        this.running++;
        task.run()
          .then(result => {
            results.push({ name: task.name, result });
            this.emit('complete', task);
          })
          .catch(err => {
            this.emit('error', task, err);
          })
          .finally(() => {
            this.running--;
          });
      }
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    return results;
  }

  getStats() {
    return {
      queued: this.queue.length,
      running: this.running,
    };
  }
}

export function createTask(name, fn) {
  return new Task(name, fn);
}
