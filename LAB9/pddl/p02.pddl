; p02.pddl - Sussman-ы хазайлт: c нь a дээр, зорилго нь a/b/c цамхаг. Оновчтой урт 6.
(define (problem blocks-p02)
  (:domain blocksworld)
  (:objects a b c - block)
  (:init (on c a) (ontable a) (ontable b)
         (clear c) (clear b)
         (handempty))
  (:goal (and (on a b) (on b c))))
