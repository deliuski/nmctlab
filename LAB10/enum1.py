# pgmpy-gui, gar-aar enumeration
import itertools

P_B = 0.001
P_E = 0.002
P_A = {(1, 1): 0.95, (1, 0): 0.94, (0, 1): 0.29, (0, 0): 0.001}
P_J = {1: 0.90, 0: 0.05}
P_M = {1: 0.70, 0: 0.01}

def pr(p1, x):
    # x=1 uyd p1, x=0 uyd 1-p1
    return p1 if x == 1 else 1 - p1

def joint(b, e, a, j, m):
    return (pr(P_B, b) * pr(P_E, e) * pr(P_A[(b, e)], a)
            * pr(P_J[a], j) * pr(P_M[a], m))

names = ['B', 'E', 'A', 'J', 'M']

def query(var, evidence):
    total = {0: 0, 1: 0}
    for combo in itertools.product([0, 1], repeat=5):
        d = dict(zip(names, combo))
        # notolgoogoor zorchildvol hayna
        if any(d[k] != v for k, v in evidence.items()):
            continue
        total[d[var]] += joint(*combo)
    s = total[0] + total[1]
    return total[1] / s   # normchilson P(var=1)

print(query('B', {'J': 1, 'M': 1}))   # 0.2842
print(query('J', {}))                 # 0.0521