module Stack where

import Data.Maybe (isNothing)

data Stack a = Stack [a]

empty :: Stack a
empty = Stack []

push :: a -> Stack a -> Stack a
push x (Stack xs) = Stack (x : xs)

pop :: Stack a -> (Maybe a, Stack a)
pop (Stack []) = (Nothing, Stack [])
pop (Stack (x:xs)) = (Just x, Stack xs)

peek :: Stack a -> Maybe a
peek (Stack []) = Nothing
peek (Stack (x:_)) = Just x

size :: Stack a -> Int
size (Stack xs) = length xs

isEmpty :: Stack a -> Bool
isEmpty (Stack xs) = null xs

class Container f where
  insert :: a -> f a -> f a
  remove :: f a -> (Maybe a, f a)

instance Container Stack where
  insert = push
  remove = pop
