type 'a tree =
  | Leaf
  | Node of 'a tree * 'a * 'a tree

let rec insert x = function
  | Leaf -> Node (Leaf, x, Leaf)
  | Node (l, v, r) ->
    if x < v then Node (insert x l, v, r)
    else if x > v then Node (l, v, insert x r)
    else Node (l, v, r)

let rec member x = function
  | Leaf -> false
  | Node (l, v, r) ->
    if x < v then member x l
    else if x > v then member x r
    else true

let rec size = function
  | Leaf -> 0
  | Node (l, _, r) -> 1 + size l + size r

let rec height = function
  | Leaf -> 0
  | Node (l, _, r) -> 1 + max (height l) (height r)

let rec to_list = function
  | Leaf -> []
  | Node (l, v, r) -> to_list l @ [v] @ to_list r

module type OrderedType = sig
  type t
  val compare : t -> t -> int
end
