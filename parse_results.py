import json
import numpy as np
import pandas as pd
import json
import os
method = 'gcg'
logdir = f'experiments/results/'

# for individual experiments
individual = True
mode = 'behaviors'

files = os.listdir(logdir)
files = [f for f in files if 'json' in f]
files = sorted(files, key=lambda x: "_".join(x.split('_')[:-1]))

max_examples = 100

logs = []
for logfile in files:
    with open(logdir+logfile, 'r') as f:
        logs.append(json.load(f))
log = logs[0]

config = log['params']
print(config.keys())

total_steps = config['n_steps']
test_steps = config.get('test_steps', 50)
log_steps = total_steps // test_steps + 1
print('log_steps', log_steps)

if individual:
    examples = 0
    test_logs = []
    control_logs = []
    goals, targets = [],[]
    for l in logs:
        sub_test_logs = l['tests']
        sub_examples = len(sub_test_logs) // log_steps
        examples += sub_examples
        test_logs.extend(sub_test_logs[:sub_examples * log_steps])
        control_logs.extend(l['controls'][:sub_examples * log_steps])
        goals.extend(l['params']['goals'][:sub_examples])
        targets.extend(l['params']['targets'][:sub_examples])
        if examples >= max_examples:
            break
else:
    test_logs = log['tests']
    examples = 1
passed, em, loss, total, controls = [],[],[],[],[]
for i in range(examples):
    sub_passed, sub_em, sub_loss, sub_total, sub_control = [],[],[],[],[]
    for res in test_logs[i*log_steps:(i+1)*log_steps]:
        sub_passed.append(res['n_passed'])
        sub_em.append(res['n_em'])
        sub_loss.append(res['n_loss'])
        sub_total.append(res['total'])
    sub_control = control_logs[i*log_steps:(i+1)*log_steps]
    passed.append(sub_passed)
    em.append(sub_em)
    loss.append(sub_loss)
    total.append(sub_total)
    controls.append(sub_control)
passed = np.array(passed)
em = np.array(em)
loss = np.array(loss)
total = np.array(total)

saved_controls = [c[-1] for c in controls]
json_obj = {
    'goal': goals,
    'target': targets,
    'controls': saved_controls
}
with open('experiments/results/individual_behavior_controls.json', 'w') as f:
    json.dump(json_obj, f)

# now run `evaluate_individual.py` with this file
