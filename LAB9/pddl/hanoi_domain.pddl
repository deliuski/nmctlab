; hanoi_domain.pddl - Нэмэлт: Hanoi цамхаг. Том зүйл дээр л тавина гэсэн дүрмийг статик smaller-аар илэрхийлнэ.
(define (domain hanoi)
  (:requirements :strips :typing)
  (:types place - object
          peg disk - place)
  (:predicates
    (on ?d - disk ?x - place)
    (clear ?x - place)
    (smaller ?x - place ?d - disk)
  )
  (:action move
    :parameters (?d - disk ?from - place ?to - place)
    :precondition (and (on ?d ?from) (clear ?d) (clear ?to) (smaller ?to ?d))
    :effect (and (on ?d ?to) (clear ?from)
                 (not (on ?d ?from)) (not (clear ?to))))
)
