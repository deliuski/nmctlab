% Лаборатори 6: Гэр бүлийн мэдлэгийн сан (Prolog хувилбар)
% Ажиллуулах: swipl family.pl  эсвэл  swish.swi-prolog.org

% ---------- Баримт ----------

male(bataa).
male(bold).
male(tomor).
male(dorj).
male(zolboo).
male(munkh).
male(temuulen).
male(bat).

female(saraa).
female(oyuna).
female(tsetseg).
female(ganaa).
female(anar).
female(naraa).
female(enkhee).

% parent(P, C): P нь C-ийн эцэг эх
parent(bataa, bold).
parent(bataa, oyuna).
parent(bataa, tomor).
parent(saraa, bold).
parent(saraa, oyuna).
parent(saraa, tomor).
parent(bold, anar).
parent(bold, zolboo).
parent(tsetseg, anar).
parent(tsetseg, zolboo).
parent(dorj, munkh).
parent(dorj, naraa).
parent(oyuna, munkh).
parent(oyuna, naraa).
parent(tomor, enkhee).
parent(ganaa, enkhee).
parent(bat, temuulen).
parent(anar, temuulen).

% ---------- Энгийн дүрэм ----------

% X нь Y-ийн эцэг
father(X, Y) :- parent(X, Y), male(X).
% X нь Y-ийн эх
mother(X, Y) :- parent(X, Y), female(X).
% X нь Y-ийн хүү
son(X, Y) :- parent(Y, X), male(X).
% X нь Y-ийн охин
daughter(X, Y) :- parent(Y, X), female(X).

% эрэгтэй эсвэл эмэгтэй бол хүн
person(X) :- male(X).
person(X) :- female(X).

% ---------- Өвөө эмээ, ах дүү ----------

% X нь Y-ийн эцэг эхийн эцэг эх
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
% нэг эцэг эхтэй, өөр хүн
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.

% ---------- Ураг төрөл ----------

brother(X, Y) :- sibling(X, Y), male(X).
sister(X, Y) :- sibling(X, Y), female(X).
% Y-ийн эцэг эхийн эрэгтэй / эмэгтэй ах дүү
uncle(X, Y) :- parent(P, Y), brother(X, P).
aunt(X, Y) :- parent(P, Y), sister(X, P).
% эцэг эхүүд нь ах дүү
cousin(X, Y) :- parent(P, X), parent(Q, Y), sibling(P, Q).

% ---------- Рекурсив дүрэм ----------

% parent-ийг рекурсийн дуудлагаас өмнө тавьсан (зүүн рекурс гогцоонд оруулна)
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
descendant(X, Y) :- ancestor(Y, X).

% ---------- Үгүйсгэл ----------

has_child(X) :- parent(X, _).
% эхлээд person(X)-ээр X-ийг холбоод дараа нь үгүйсгэнэ
childless(X) :- person(X), \+ has_child(X).
great_grandparent(X, Y) :- parent(X, Z), grandparent(Z, Y).

% ---------- Нэмэлт: хуримын ураг ----------

spouse(X, Y) :- parent(X, Z), parent(Y, Z), X \= Y.
uncle_in_law(X, Y) :- aunt(Z, Y), spouse(X, Z).
aunt_in_law(X, Y) :- uncle(Z, Y), spouse(X, Z).

% ---------- Шалгах асуултууд ----------
% ?- findall(P-C, parent(P, C), L), length(L, N).        N = 18
% ?- ancestor(bataa, temuulen).                          true
% ?- childless(temuulen).                                true
% ?- childless(bataa).                                   false
% ?- findall(Y, sibling(oyuna, Y), L), length(L, N).     N = 4
% ?- findall(Y, sibling(oyuna, Y), L), sort(L, S).       S = [bold, tomor]
% ?- setof(X, childless(X), L).                          5 хүн
