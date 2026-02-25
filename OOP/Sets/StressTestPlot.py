import random
import time
import matplotlib.pyplot as plt
import sys
sys.path.append('.')
from IntSet import IntSet
from JendaHashSet import SimpleHashSet
from CuckooHashSet import CuckooHashSet
from AbstractSet import BuiltInSet
from Honza import Set as HonzaSet
# from ChristianSetImplement import set as ChristianSet

implementations = [
    ("Int", IntSet),
    ("Hash", SimpleHashSet),
    ("Cuckoo", CuckooHashSet),
    ("BuiltIn", BuiltInSet),
    ("List", HonzaSet)
    # ("ChristianSet", ChristianSet),
]

N_values = [10_000 * i for i in range(1, 21)]

categories = ['insertion', 'removal', 'contains', 'union', 'intersection']
import numpy as np

results = {cat: {name: [] for name, _ in implementations} for cat in categories}
errors = {cat: {name: [] for name, _ in implementations} for cat in categories}
num_runs = 5

for name, impl in implementations:
    for N in N_values:
        timings = {cat: [] for cat in categories}
        for _ in range(num_runs):
            RANGE = 2 * N
            set1_elements = random.sample(range(RANGE), N)
            set2_elements = random.sample(range(RANGE), N)

            # Insertion
            start = time.time()
            set1 = impl()
            for x in set1_elements:
                set1.add(x)
            end = time.time()
            timings['insertion'].append(end - start)

            # Insertion set2
            set2 = impl()
            for x in set2_elements:
                set2.add(x)

            # Contains
            check_elements = random.sample(set1_elements, min(1000, N)) + random.sample(range(RANGE), min(1000, N))
            random.shuffle(check_elements)
            start = time.time()
            _ = [set1.contains(x) for x in check_elements]
            end = time.time()
            timings['contains'].append(end - start)

            # Union
            start = time.time()
            _ = set1.union(set2)
            end = time.time()
            timings['union'].append(end - start)

            # Intersection
            start = time.time()
            _ = set1.intersection(set2)
            end = time.time()
            timings['intersection'].append(end - start)

            # Removal
            remove_elements = random.sample(set1_elements, min(1000, N))
            start = time.time()
            for x in remove_elements:
                set1.remove(x)
            end = time.time()
            timings['removal'].append(end - start)

        for cat in categories:
            mean = np.mean(timings[cat])
            min_val = np.min(timings[cat])
            max_val = np.max(timings[cat])
            results[cat][name].append(mean)
            errors[cat][name].append([[mean - min_val], [max_val - mean]])

# Plotting
import os
plot_dir_log = 'plots'
plot_dir_linear = 'plots_linear'
os.makedirs(plot_dir_log, exist_ok=True)
os.makedirs(plot_dir_linear, exist_ok=True)

for cat in categories:
    # Log scale plot
    plt.figure(figsize=(12, 8))
    for name, _ in implementations:
        # Convert error bars to proper format for matplotlib
        err = np.array(errors[cat][name]).T.squeeze()
        plt.errorbar(N_values, results[cat][name], yerr=err, label=name, capsize=5)
    plt.xlabel('N (number of elements)')
    plt.ylabel('Time (seconds)')
    plt.title(f'Set Implementations Comparison: {cat.capitalize()} (log scale)')
    plt.legend()
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True)
    plt.tight_layout()
    plot_path_log = os.path.join(plot_dir_log, f'{cat}_comparison_log.png')
    plt.savefig(plot_path_log)
    plt.close()

    # Linear scale plot
    plt.figure(figsize=(12, 8))
    for name, _ in implementations:
        err = np.array(errors[cat][name]).T.squeeze()
        plt.errorbar(N_values, results[cat][name], yerr=err, label=name, capsize=5)
    plt.xlabel('N (number of elements)')
    plt.ylabel('Time (seconds)')
    plt.title(f'Set Implementations Comparison: {cat.capitalize()} (linear scale)')
    plt.legend()
    plt.xscale('linear')
    plt.yscale('linear')
    plt.grid(True)
    plt.tight_layout()
    plot_path_linear = os.path.join(plot_dir_linear, f'{cat}_comparison_linear.png')
    plt.savefig(plot_path_linear)
    plt.close()