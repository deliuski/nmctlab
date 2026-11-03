; lp02.pddl - Хоёр ачаа эсрэг чиглэлд: pkg1 c1-1 -> c2-1, pkg2 c2-1 -> c1-2. Оновчтой урт 18.
(define (problem logistics-lp02)
  (:domain logistics)
  (:objects city1 city2 - city
            c1-1 c1-2 c2-1 - location
            a1 a2 - airport
            t1 t2 - truck
            plane1 - airplane
            pkg1 pkg2 - package)
  (:init (in-city c1-1 city1) (in-city c1-2 city1) (in-city a1 city1)
         (in-city c2-1 city2) (in-city a2 city2)
         (at t1 c1-1) (at t2 c2-1) (at plane1 a1)
         (at pkg1 c1-1) (at pkg2 c2-1))
  (:goal (and (at pkg1 c2-1) (at pkg2 c1-2))))
