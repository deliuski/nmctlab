; lp03.pddl - Нэмэлт: гурван ачаатай Logistics, city2-т c2-2 нэмэгдсэн. Хүлээгдэх оновчтой урт 26.
(define (problem logistics-lp03)
  (:domain logistics)
  (:objects city1 city2 - city
            c1-1 c1-2 c2-1 c2-2 - location
            a1 a2 - airport
            t1 t2 - truck
            plane1 - airplane
            pkg1 pkg2 pkg3 - package)
  (:init (in-city c1-1 city1) (in-city c1-2 city1) (in-city a1 city1)
         (in-city c2-1 city2) (in-city c2-2 city2) (in-city a2 city2)
         (at t1 c1-1) (at t2 c2-1) (at plane1 a1)
         (at pkg1 c1-1) (at pkg2 c2-1) (at pkg3 c1-2))
  (:goal (and (at pkg1 c2-2) (at pkg2 c1-2) (at pkg3 c2-1))))
