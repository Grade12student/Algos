'''
 didn't set up explicit node groups 
 because Epidemic Replication typically involves nodes randomly communicating with each other, 
 so there are no predefined groups like in some other replication algorithms.
 '''
import simpy
import random

# Constants
NUM_NODES = 100
NUM_CLIENT_REQUESTS = 10000

class EpidemicReplication:
    def __init__(self, env, nodes):
        self.env = env
        self.nodes = nodes
        self.latency = {}  # dict to store latencies
        self.total_network_overhead = 0
        self.env.process(self.run())

    def run(self):
        while True:
            # Simulate request
            request_time = self.env.now
            latency = random.uniform(1, 10)
            yield self.env.timeout(latency)
            self.latency[request_time] = self.env.now - request_time

            # Simulate network overhead (gossip)
            for node in self.nodes:
                if node != self:
                    network_overhead = random.uniform(0.1, 1.0)
                    self.total_network_overhead += network_overhead
                    yield self.env.timeout(network_overhead)

# Simulation    
env = simpy.Environment()
nodes = [EpidemicReplication(env, []) for _ in range(NUM_NODES)]
for node in nodes:
    node.nodes = nodes  # Set all nodes as neighbors

env.run(until=NUM_CLIENT_REQUESTS)

# Calculate statistics
total_latency = sum(node.latency.values())
average_latency = total_latency / NUM_CLIENT_REQUESTS
average_network_overhead = sum(node.total_network_overhead for node in nodes) / NUM_CLIENT_REQUESTS

# Calculate availability per replica group
availability_per_group = [
    sum(node.latency.values()) / NUM_CLIENT_REQUESTS
    for node in nodes
]

# Calculate overall availability
overall_availability = sum(availability_per_group) / NUM_NODES

# Print statistics
print(f"1. Average Latency: {average_latency:.3f} ms")
print(f"2. Overall Availability: {overall_availability:.3%}")
print(f"3. Availability per Replica Group: {availability_per_group}")
print(f"4. Average Network Overhead per Request: {average_network_overhead:.3f} MB")
