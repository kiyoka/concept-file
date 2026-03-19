module Hello where

greet :: String -> String
greet name = "Hello, " ++ name ++ "!"

add :: Int -> Int -> Int
add x y = x + y

main :: IO ()
main = putStrLn (greet "World")
