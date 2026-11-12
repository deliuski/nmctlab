# Alarm setgel pgmpy-aar
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

model = DiscreteBayesianNetwork([('Burglary', 'Alarm'), ('Earthquake', 'Alarm'),
                                 ('Alarm', 'JohnCalls'), ('Alarm', 'MaryCalls')])

cpd_b = TabularCPD('Burglary', 2, [[0.999], [0.001]])
cpd_e = TabularCPD('Earthquake', 2, [[0.998], [0.002]])

# bagana: (B,E) = (0,0), (0,1), (1,0), (1,1)
cpd_a = TabularCPD('Alarm', 2,
                   [[0.999, 0.71, 0.06, 0.05],
                    [0.001, 0.29, 0.94, 0.95]],
                   evidence=['Burglary', 'Earthquake'], evidence_card=[2, 2])

cpd_j = TabularCPD('JohnCalls', 2, [[0.95, 0.10], [0.05, 0.90]],
                   evidence=['Alarm'], evidence_card=[2])
cpd_m = TabularCPD('MaryCalls', 2, [[0.99, 0.30], [0.01, 0.70]],
                   evidence=['Alarm'], evidence_card=[2])

model.add_cpds(cpd_b, cpd_e, cpd_a, cpd_j, cpd_m)
print(model.check_model())

infer = VariableElimination(model)

# prior
for v in ['JohnCalls', 'MaryCalls', 'Alarm']:
    print(v, infer.query([v]).values[1])

# posterior
print(infer.query(['Burglary'], evidence={'JohnCalls': 1}).values[1])
print(infer.query(['Burglary'], evidence={'JohnCalls': 1, 'MaryCalls': 1}).values[1])
print(infer.query(['Earthquake'], evidence={'JohnCalls': 1, 'MaryCalls': 1}).values[1])
print(infer.query(['Alarm'], evidence={'JohnCalls': 1, 'MaryCalls': 1}).values[1])
print(infer.query(['Burglary'], evidence={'JohnCalls': 1, 'MaryCalls': 0}).values[1])
print(infer.query(['JohnCalls'], evidence={'Burglary': 1}).values[1])

# explaining away
print(infer.query(['Burglary'], evidence={'Alarm': 1}).values[1])
print(infer.query(['Burglary'], evidence={'Alarm': 1, 'Earthquake': 1}).values[1])
print(infer.query(['Burglary'], evidence={'Alarm': 1, 'Earthquake': 0}).values[1])

# hamaaral
print(model.active_trail_nodes('Burglary'))
print(model.active_trail_nodes('Burglary', observed=['Alarm']))
print(model.local_independencies('JohnCalls'))

# Step 8: forward ба rejection sampling (rejection-ийг өөрөө бичсэн)
from pgmpy.sampling import BayesianModelSampling

sampler = BayesianModelSampling(model)

for n in [1000, 10000, 100000]:
    # n түүврийг prior-оор гаргана
    data = sampler.forward_sample(size=n, seed=1, show_progress=False)
    p_j = data['JohnCalls'].mean()          # P(J=1)

    # нотолгоо (J=1, M=1)-тэй таарсныг л үлдээнэ
    acc = data[(data['JohnCalls'] == 1) & (data['MaryCalls'] == 1)]
    k = len(acc)                             # хүлээн авсан түүвэр
    p_b = acc['Burglary'].mean() if k > 0 else float('nan')

    print(n, round(p_j, 4), k, round(p_b, 4))