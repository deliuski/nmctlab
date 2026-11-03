; p04.pddl - Таван блоктой a/b/c/d/e цамхгийг урвуулж e/d/c/b/a болгоно. Оновчтой урт 10.
(define (problem blocks-p04)
  (:domain blocksworld)
  (:objects a b c d e - block)
  (:init (on a b) (on b c) (on c d) (on d e) (ontable e)
         (clear a)
         (handempty))
  (:goal (and (on e d) (on d c) (on c b) (on b a))))
