#include <cmath>
#include <iostream>

class Point {
public:
    double x, y;

    Point(double x, double y) : x(x), y(y) {}

    double distance(const Point& other) const {
        return std::sqrt(std::pow(x - other.x, 2) + std::pow(y - other.y, 2));
    }

    void print() const {
        std::cout << "(" << x << ", " << y << ")" << std::endl;
    }
};

int main() {
    Point a(0, 0), b(3, 4);
    std::cout << a.distance(b) << std::endl;
    return 0;
}
