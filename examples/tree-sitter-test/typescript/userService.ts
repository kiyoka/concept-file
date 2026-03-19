interface User {
  id: number;
  name: string;
  email: string;
}

type Role = 'admin' | 'editor' | 'viewer';

enum Status {
  Active,
  Inactive,
  Banned,
}

class UserService {
  private users: Map<number, User> = new Map();

  create(name: string, email: string): User {
    const id = this.users.size + 1;
    const user: User = { id, name, email };
    this.users.set(id, user);
    return user;
  }

  findById(id: number): User | undefined {
    return this.users.get(id);
  }

  findByEmail(email: string): User | undefined {
    for (const user of this.users.values()) {
      if (user.email === email) return user;
    }
    return undefined;
  }

  delete(id: number): boolean {
    return this.users.delete(id);
  }

  listAll(): User[] {
    return Array.from(this.users.values());
  }
}

export function createUserService(): UserService {
  return new UserService();
}
