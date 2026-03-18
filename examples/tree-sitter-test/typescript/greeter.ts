interface Greeting {
  message: string;
  timestamp: Date;
}

function createGreeting(name: string): Greeting {
  return {
    message: `Hello, ${name}!`,
    timestamp: new Date(),
  };
}

export { Greeting, createGreeting };
