#import <Foundation/Foundation.h>

@interface Greeter : NSObject
@property (nonatomic, strong) NSString *name;
- (NSString *)greet;
@end

@implementation Greeter
- (NSString *)greet {
    return [NSString stringWithFormat:@"Hello, %@!", self.name];
}
@end

int main() {
    Greeter *g = [[Greeter alloc] init];
    g.name = @"World";
    NSLog(@"%@", [g greet]);
    return 0;
}
