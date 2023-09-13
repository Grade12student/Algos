import simpy
import random

# Constants
NUM_NODES = 9
NUM_REPLICA_GROUPS = 3
NUM_CLIENT_REQUESTS = 10000

class Node:
    def __init__(self, id):
        self.id = id
        self.failed = False
        self.requests_handled = 0

class ChainReplication:

    def __init__(self, env, nodes):
        self.env = env
        self.nodes = nodes
        self.head = nodes[0]
        self.tail = nodes[-1]
        self.latency = {}  # dict to store latencies
        self.total_network_overhead = 0
        self.env.process(self.run())

    def reconstruct(self):
        # Reconstruct chain
        self.nodes.sort(key=lambda n: n.id)
        for i in range(len(self.nodes) - 1):
            self.nodes[i].next = self.nodes[i+1]
        self.head = self.nodes[0]
        self.tail = self.nodes[-1]

    def run(self):
        while True:
            # Simulate request
            request_time = self.env.now
            latency = random.uniform(1, 10)
            yield self.env.timeout(latency)
            self.latency[request_time] = self.env.now - request_time
            
            # Simulate network overhead
            network_overhead = random.uniform(0.1, 1.0)
            self.total_network_overhead += network_overhead

            # Check for failures
            for n in self.nodes:
                if random.random() < 0.1:
                    n.failed = True
                    self.reconstruct()
                elif n.failed:
                    n.failed = False
                    self.reconstruct()

# Simulation    
env = simpy.Environment()
nodes = [Node(i) for i in range(NUM_NODES)]
chain = ChainReplication(env, nodes)
env.run(until=NUM_CLIENT_REQUESTS)

# Calculate availability per replica group
availability_per_group = [
    len([n for n in nodes if not n.failed and n.id % NUM_REPLICA_GROUPS == group]) / len(nodes)
    for group in range(NUM_REPLICA_GROUPS)
]

# Stats
total_latency = sum(chain.latency.values())
average_latency = total_latency / NUM_CLIENT_REQUESTS
availability = len([n for n in nodes if not n.failed]) / len(nodes)
average_network_overhead = chain.total_network_overhead / NUM_CLIENT_REQUESTS

print(f"1. Average Latency: {average_latency:.3f} ms")
print(f"2. Availability: {availability:.3%}")
print(f"3. Availability per Replica Group: {availability_per_group}")
print(f"4. Average Network Overhead per Request: {average_network_overhead:.3f} MB")

