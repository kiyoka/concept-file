let greet name =
  "Hello, " ^ name ^ "!"

let add x y = x + y

let () =
  let msg = greet "World" in
  print_endline msg;
  Printf.printf "%d\n" (add 3 4)
