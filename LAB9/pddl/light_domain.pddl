; light_domain.pddl - Гэрэл асаах хамгийн жижиг domain (Алхам 1)
(define (domain light)
  (:requirements :strips)
  (:predicates (on ?l) (off ?l))
  (:action turn-on
    :parameters (?l)
    :precondition (off ?l)
    :effect (and (on ?l) (not (off ?l)))))
