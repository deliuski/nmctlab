
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDDL = os.path.join(HERE, "pddl")


def facts(*items):
    """('on a b', 'handempty') -> {('on','a','b'), ('handempty',)}"""
    return {tuple(s.split()) for s in items}


# GOl functions 

def applicable(state, pre):
    return pre <= state


def apply(state, add, delete):
    # Ehleed delete iig hasaad add iig nemne
    return frozenset((state - delete) | add)


def make_action(name, args):
    """Үйлдлийн нэр, аргументаас (precondition, add, delete) гурвыг үүсгэнэ."""
    if name not in ACTIONS:
        raise ValueError(f"тодорхойгүй үйлдэл: {name}")
    return ACTIONS[name](*args)


def parse_plan(path):
    """'(pick-up b)' мөр бүрийг ('pick-up', ('b',)) болгоно."""
    plan = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            parts = line.strip("()").split()
            plan.append((parts[0], tuple(parts[1:])))
    return plan


def show(step):
    return "(" + " ".join((step[0],) + tuple(step[1])) + ")"


def check(init, goal, plan):
    """Үйлдлийг дараалан хэрэгжүүлж, зөв бол True буцаана."""
    state = frozenset(init)
    for i, step in enumerate(plan):
        try:
            pre, add, delete = make_action(step[0], step[1])
        except (ValueError, TypeError) as e:
            print(f"  БУРУУ: {i}-р алхамд {show(step)} үйлдэл алдаатай: {e}")
            return False
        if not applicable(state, pre):
            missing = sorted(" ".join(f) for f in pre - state)
            print(f"  БУРУУ: {i}-р алхамд {show(step)} үйлдлийн precondition биелээгүй. "
                  f"Дутуу: {missing}")
            return False
        state = apply(state, add, delete)
    missing = sorted(" ".join(f) for f in goal - state)
    if missing:
        print(f"  БУРУУ: {len(plan)} үйлдлийн дараа зорилго биелээгүй. Дутуу: {missing}")
        return False
    print(f"  ЗӨВ: {len(plan)} үйлдэл, зорилго биелсэн")
    return True


#blockworld alham 2 husnegt

def pick_up(x):
    return (facts(f"ontable {x}", f"clear {x}", "handempty"),
            facts(f"holding {x}"),
            facts(f"ontable {x}", f"clear {x}", "handempty"))


def put_down(x):
    return (facts(f"holding {x}"),
            facts(f"ontable {x}", f"clear {x}", "handempty"),
            facts(f"holding {x}"))


def stack(x, y):
    return (facts(f"holding {x}", f"clear {y}"),
            facts(f"on {x} {y}", f"clear {x}", "handempty"),
            facts(f"holding {x}", f"clear {y}"))


def unstack(x, y):
    return (facts(f"on {x} {y}", f"clear {x}", "handempty"),
            facts(f"holding {x}", f"clear {y}"),
            facts(f"on {x} {y}", f"clear {x}", "handempty"))


#logistics alham 8 husnegt

def load(pkg, veh, loc):
    return facts(f"at {veh} {loc}", f"at {pkg} {loc}"), facts(f"in {pkg} {veh}"), facts(f"at {pkg} {loc}")


def unload(pkg, veh, loc):
    return facts(f"at {veh} {loc}", f"in {pkg} {veh}"), facts(f"at {pkg} {loc}"), facts(f"in {pkg} {veh}")


def drive_truck(truck, frm, to, c):
    return (facts(f"at {truck} {frm}", f"in-city {frm} {c}", f"in-city {to} {c}"),
            facts(f"at {truck} {to}"),
            facts(f"at {truck} {frm}"))


def fly_airplane(plane, frm, to):
    return facts(f"at {plane} {frm}"), facts(f"at {plane} {to}"), facts(f"at {plane} {frm}")


#hanoi nemelt daalgavar

def move(d, frm, to):
    return (facts(f"on {d} {frm}", f"clear {d}", f"clear {to}", f"smaller {to} {d}"),
            facts(f"on {d} {to}", f"clear {frm}"),
            facts(f"on {d} {frm}", f"clear {to}"))


ACTIONS = {
    "pick-up": pick_up, "put-down": put_down, "stack": stack, "unstack": unstack,
    "load-truck": load, "unload-truck": unload, "drive-truck": drive_truck,
    "load-airplane": load, "unload-airplane": unload, "fly-airplane": fly_airplane,
    "move": move,
}

#bodloguud 

def tower(*blocks):
    """tower('a','b','c') -> a нь b дээр, b нь c дээр, c ширээн дээр, a чөлөөтэй, гар хоосон."""
    on = {f"on {x} {y}" for x, y in zip(blocks, blocks[1:])}
    return facts(*on, f"clear {blocks[0]}", f"ontable {blocks[-1]}", "handempty")


def logistics_init(*packages, extra=()):
    cities = ["in-city c1-1 city1", "in-city c1-2 city1", "in-city a1 city1",
              "in-city c2-1 city2", "in-city a2 city2"]
    return facts(*cities, *extra, "at t1 c1-1", "at t2 c2-1", "at plane1 a1", *packages)


def hanoi_init(n):
    disks = [f"d{i}" for i in range(1, n + 1)]
    pegs = ["peg1", "peg2", "peg3"]
    s = [f"smaller {p} {d}" for p in pegs for d in disks]
    s += [f"smaller {disks[j]} {disks[i]}" for i in range(n) for j in range(i + 1, n)]
    s += [f"on {disks[i]} {disks[i + 1]}" for i in range(n - 1)]
    s += [f"on {disks[-1]} peg1", "clear d1", "clear peg2", "clear peg3"]
    return facts(*s)


def hanoi_goal(n):
    disks = [f"d{i}" for i in range(1, n + 1)]
    return facts(*[f"on {disks[i]} {disks[i + 1]}" for i in range(n - 1)], f"on {disks[-1]} peg3")


PROBLEMS = {
    "p01": (facts("ontable a", "ontable b", "ontable c", "clear a", "clear b", "clear c", "handempty"),
            facts("on a b", "on b c")),
    "p02": (facts("on c a", "ontable a", "ontable b", "clear c", "clear b", "handempty"),
            facts("on a b", "on b c")),
    "p03": (tower("a", "b", "c", "d"), facts("on d c", "on c b", "on b a")),
    "p04": (tower("a", "b", "c", "d", "e"), facts("on e d", "on d c", "on c b", "on b a")),
    "lp01": (logistics_init("at pkg1 c1-1"), facts("at pkg1 c2-1")),
    "lp02": (logistics_init("at pkg1 c1-1", "at pkg2 c2-1"), facts("at pkg1 c2-1", "at pkg2 c1-2")),
    "lp03": (logistics_init("at pkg1 c1-1", "at pkg2 c2-1", "at pkg3 c1-2", extra=["in-city c2-2 city2"]),
             facts("at pkg1 c2-2", "at pkg2 c1-2", "at pkg3 c2-1")),
    "hanoi3": (hanoi_init(3), hanoi_goal(3)),
    "hanoi4": (hanoi_init(4), hanoi_goal(4)),
}

# test
BAD_PLANS = [
    ("p01", [("stack", ("a", "b"))], "гарт юу ч алга"),
    ("p01", [("pick-up", ("a",)), ("pick-up", ("b",))], "гар хоёр блок барьж чадахгүй"),
    ("p01", [("pick-up", ("b",)), ("stack", ("b", "c"))], "зорилгын хагас л биелнэ"),
    ("lp01", [("load-truck", ("pkg1", "t2", "c1-1"))], "t2 машин c1-1 дээр байхгүй"),
    ("lp01", [("drive-truck", ("t1", "c1-1", "a2", "city1"))], "машин хот хооронд явахгүй"),
    ("hanoi3", [("move", ("d3", "peg1", "peg3"))], "d3-ийн дээр диск байна"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) == 3:
        init, goal = PROBLEMS[sys.argv[1]]
        print(f"{sys.argv[1]} <- {sys.argv[2]}")
        ok = check(init, goal, parse_plan(sys.argv[2]))
        sys.exit(0 if ok else 1)

    all_ok = True
    print("=== pyperplan-ын төлөвлөгөөнүүд (зөв гэж хүлээгдэнэ) ===")
    for name, (init, goal) in PROBLEMS.items():
        path = os.path.join(PDDL, f"{name}.pddl.soln")
        print(f"{name}:")
        if not os.path.exists(path):
            print("  .soln файл алга")
            all_ok = False
            continue
        all_ok &= check(init, goal, parse_plan(path))

    print("\n=== Буруу төлөвлөгөөнүүд (няцаагдана гэж хүлээгдэнэ) ===")
    for name, plan, why in BAD_PLANS:
        print(f"{name}: {' '.join(show(s) for s in plan)}  # {why}")
        init, goal = PROBLEMS[name]
        all_ok &= not check(init, goal, plan)

    print("\nДҮН:", "бүх шалгалт хүлээгдсэнээр гарлаа" if all_ok else "ЗӨРҮҮ БАЙНА")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
