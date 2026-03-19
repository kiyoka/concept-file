const std = @import("std");

const Point = struct {
    x: f64,
    y: f64,

    fn distance(self: Point, other: Point) f64 {
        const dx = self.x - other.x;
        const dy = self.y - other.y;
        return @sqrt(dx * dx + dy * dy);
    }
};

pub fn main() void {
    const a = Point{ .x = 0, .y = 0 };
    const b = Point{ .x = 3, .y = 4 };
    std.debug.print("{d}\n", .{a.distance(b)});
}
