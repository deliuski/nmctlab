; logistics_domain.pddl - Logistics: ачааг машинаар хотын дотор, онгоцоор хот хооронд зөөнө (Алхам 8)
(define (domain logistics)
  (:requirements :strips :typing)
  (:types city location physobj - object
          airport - location
          vehicle package - physobj
          truck airplane - vehicle)
  (:predicates
    (in-city ?loc - location ?c - city)
    (at ?obj - physobj ?loc - location)
    (in ?pkg - package ?veh - vehicle)
  )
  (:action load-truck
    :parameters (?pkg - package ?truck - truck ?loc - location)
    :precondition (and (at ?truck ?loc) (at ?pkg ?loc))
    :effect (and (in ?pkg ?truck) (not (at ?pkg ?loc))))
  (:action unload-truck
    :parameters (?pkg - package ?truck - truck ?loc - location)
    :precondition (and (at ?truck ?loc) (in ?pkg ?truck))
    :effect (and (at ?pkg ?loc) (not (in ?pkg ?truck))))
  (:action drive-truck
    :parameters (?truck - truck ?from - location ?to - location ?c - city)
    :precondition (and (at ?truck ?from) (in-city ?from ?c) (in-city ?to ?c))
    :effect (and (at ?truck ?to) (not (at ?truck ?from))))
  (:action load-airplane
    :parameters (?pkg - package ?plane - airplane ?loc - location)
    :precondition (and (at ?plane ?loc) (at ?pkg ?loc))
    :effect (and (in ?pkg ?plane) (not (at ?pkg ?loc))))
  (:action unload-airplane
    :parameters (?pkg - package ?plane - airplane ?loc - location)
    :precondition (and (at ?plane ?loc) (in ?pkg ?plane))
    :effect (and (at ?pkg ?loc) (not (in ?pkg ?plane))))
  (:action fly-airplane
    :parameters (?plane - airplane ?from - airport ?to - airport)
    :precondition (and (at ?plane ?from))
    :effect (and (at ?plane ?to) (not (at ?plane ?from))))
)
