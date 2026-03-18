#import <Foundation/Foundation.h>

@protocol Speakable
- (NSString *)speak;
@end

@interface Animal : NSObject <Speakable>
@property (nonatomic, strong) NSString *name;
@property (nonatomic, assign) NSInteger age;
- (instancetype)initWithName:(NSString *)name age:(NSInteger)age;
- (void)eat:(NSString *)food;
@end

@implementation Animal

- (instancetype)initWithName:(NSString *)name age:(NSInteger)age {
    self = [super init];
    if (self) {
        _name = name;
        _age = age;
    }
    return self;
}

- (NSString *)speak {
    return [NSString stringWithFormat:@"%@ says hello", self.name];
}

- (void)eat:(NSString *)food {
    NSLog(@"%@ eats %@", self.name, food);
}

@end
