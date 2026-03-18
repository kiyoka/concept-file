#include <stdio.h>

struct Point {
    int x;
    int y;
};

int add(int a, int b) {
    return a + b;
}

void print_point(struct Point p) {
    printf("(%d, %d)\n", p.x, p.y);
}

int main() {
    struct Point p = {3, 4};
    print_point(p);
    return 0;
}
