const std = @import("std");
const Allocator = std.mem.Allocator;

pub const PoolAllocator = struct {
    backing: Allocator,
    pool: []u8,
    offset: usize,

    pub fn init(backing: Allocator, size: usize) !PoolAllocator {
        const pool = try backing.alloc(u8, size);
        return PoolAllocator{
            .backing = backing,
            .pool = pool,
            .offset = 0,
        };
    }

    pub fn alloc(self: *PoolAllocator, size: usize) ?[]u8 {
        if (self.offset + size > self.pool.len) return null;
        const result = self.pool[self.offset .. self.offset + size];
        self.offset += size;
        return result;
    }

    pub fn reset(self: *PoolAllocator) void {
        self.offset = 0;
    }

    pub fn deinit(self: *PoolAllocator) void {
        self.backing.free(self.pool);
    }
};

pub fn createPool(size: usize) !PoolAllocator {
    return PoolAllocator.init(std.heap.page_allocator, size);
}

test "pool allocator" {
    var pool = try createPool(1024);
    defer pool.deinit();

    const buf = pool.alloc(64) orelse unreachable;
    try std.testing.expect(buf.len == 64);
}
