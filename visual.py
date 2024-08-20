import matplotlib.pyplot as plt
import numpy as np

# Data
algorithms = ['Chain', 'Chord', 'Epidemic', 'Paxos', 'Primary-Backup']
latencies = [5.425, 0.000897, 5.507, 0.001, 11.44]  # in ms
availabilities = [0.531, 33.00, 94.000, 8.00, 90.23]  # in %
overheads = [0.101, 0.002928, 25.112, 0, 61.295]  # in MB

# 1. Bar Chart for Average Latency
plt.figure(figsize=(10, 6))
plt.bar(algorithms, latencies)
plt.title('Average Latency Comparison')
plt.ylabel('Latency (ms)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2. Bar Chart for Overall Availability
plt.figure(figsize=(10, 6))
plt.bar(algorithms, availabilities)
plt.title('Overall Availability Comparison')
plt.ylabel('Availability (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 3. Stacked Bar Chart for Availability per Replica Group
chain_availability = [0.0107, 0.0, 0.0032, 0.0, 0.0091, 0.0058, 0.009, 0.0113, 0.0017, 0.0023]
pb_availability = [1.537, 1.512, 1.544, 1.558, 1.577, 1.519, 1.535, 1.57, 1.527, 1.528]

plt.figure(figsize=(10, 6))
plt.bar(range(10), chain_availability, label='Chain')
plt.bar(range(10), pb_availability, bottom=chain_availability, label='Primary-Backup')
plt.title('Availability per Replica Group')
plt.xlabel('Replica Group')
plt.ylabel('Availability')
plt.legend()
plt.tight_layout()
plt.show()

# 4. Bar Chart for Average Network Overhead
plt.figure(figsize=(10, 6))
plt.bar(algorithms, overheads)
plt.title('Average Network Overhead per Request')
plt.ylabel('Overhead (MB)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 5. Scatter Plot for Latency vs. Availability
plt.figure(figsize=(10, 6))
plt.scatter(latencies, availabilities)
for i, alg in enumerate(algorithms):
    plt.annotate(alg, (latencies[i], availabilities[i]))
plt.title('Latency vs. Availability')
plt.xlabel('Latency (ms)')
plt.ylabel('Availability (%)')
plt.tight_layout()
plt.show()