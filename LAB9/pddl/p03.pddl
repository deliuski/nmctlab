; p03.pddl - Дөрвөн блоктой a/b/c/d цамхгийг урвуулж d/c/b/a болгоно. Оновчтой урт 8.
(define (problem blocks-p03)
  (:domain blocksworld)
  (:objects a b c d - block)
  (:init (on a b) (on b c) (on c d) (ontable d)
         (clear a)
         (handempty))
  (:goal (and (on d c) (on c b) (on b a))))
