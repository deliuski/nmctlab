; lp01.pddl - Нэг ачааг city1-ийн c1-1-ээс city2-ын c2-1 рүү хүргэнэ. Оновчтой урт 10.
(define (problem logistics-lp01)
  (:domain logistics)
  (:objects city1 city2 - city
            c1-1 c1-2 c2-1 - location
            a1 a2 - airport
            t1 t2 - truck
            plane1 - airplane
            pkg1 - package)
  (:init (in-city c1-1 city1) (in-city c1-2 city1) (in-city a1 city1)
         (in-city c2-1 city2) (in-city a2 city2)
         (at t1 c1-1) (at t2 c2-1) (at plane1 a1)
         (at pkg1 c1-1))
  (:goal (and (at pkg1 c2-1))))
