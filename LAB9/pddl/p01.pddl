; p01.pddl - Гурван блок ширээн дээр, зорилго нь a/b/c цамхаг. Оновчтой урт 4.
(define (problem blocks-p01)
  (:domain blocksworld)
  (:objects a b c - block)
  (:init (ontable a) (ontable b) (ontable c)
         (clear a) (clear b) (clear c)
         (handempty))
  (:goal (and (on a b) (on b c))))
