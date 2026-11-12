import itertools
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# --- pgmpy хэсэг ---
model = DiscreteBayesianNetwork([('Sleep', 'Exam'), ('Study', 'Exam'), ('Exam', 'Stress')])

cpd_s = TabularCPD('Sleep', 2, [[0.4], [0.6]])
cpd_t = TabularCPD('Study', 2, [[0.5], [0.5]])
# багана: (S,T) = (0,0), (0,1), (1,0), (1,1)
cpd_e = TabularCPD('Exam', 2,
                   [[0.9, 0.4, 0.6, 0.1],
                    [0.1, 0.6, 0.4, 0.9]],
                   evidence=['Sleep', 'Study'], evidence_card=[2, 2])
cpd_r = TabularCPD('Stress', 2, [[0.3, 0.8], [0.7, 0.2]],
                   evidence=['Exam'], evidence_card=[2])
model.add_cpds(cpd_s, cpd_t, cpd_e, cpd_r)
print(model.check_model())

infer = VariableElimination(model)
print(infer.query(['Exam']).values[1])                                        # prior
print(infer.query(['Study'], evidence={'Exam': 0}).values[1])                 # diagnostic
print(infer.query(['Study'], evidence={'Exam': 0, 'Sleep': 1}).values[1])     # explaining away
print(infer.query(['Study'], evidence={'Exam': 0, 'Sleep': 0}).values[1])

# --- enumeration хэсэг ---
PS, PT = 0.6, 0.5
PE = {(0, 0): 0.1, (0, 1): 0.6, (1, 0): 0.4, (1, 1): 0.9}
PR = {1: 0.2, 0: 0.7}
pr = lambda p, x: p if x else 1 - p

def joint(s, t, e, r):
    return pr(PS, s) * pr(PT, t) * pr(PE[(s, t)], e) * pr(PR[e], r)

names = ['S', 'T', 'E', 'R']

def query(var, evidence):
    tot = [0, 0]
    for c in itertools.product([0, 1], repeat=4):
        d = dict(zip(names, c))
        if any(d[k] != v for k, v in evidence.items()):
            continue
        tot[d[var]] += joint(*c)
    return tot[1] / sum(tot)

print(query('E', {}))
print(query('T', {'E': 0}))
print(query('T', {'E': 0, 'S': 1}))
print(query('T', {'E': 0, 'S': 0}))