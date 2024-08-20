import simpy
import random

# Constants
NUM_NODES = 100
NUM_REPLICA_GROUPS = 10
NUM_CLIENT_REQUESTS = 10000

class Node:
    def __init__(self, id, group):
        self.id = id
        self.group = group
        self.failed = False
        self.requests_handled = 0
        self.next = None

class ChainReplication:

    def __init__(self, env, nodes):
        self.env = env
        self.nodes = nodes
        self.chains = [[] for _ in range(NUM_REPLICA_GROUPS)]
        self.latency = {}  # dict to store latencies
        self.total_network_overhead = 0
        self.construct_chains()
        self.env.process(self.run())
        

    def construct_chains(self):
        for node in self.nodes:
            chain = self.chains[node.group]
            if chain:
                chain[-1].next = node
            chain.append(node)

    def reconstruct(self):
        for chain in self.chains:
            chain[:] = [n for n in chain if not n.failed]
            for i in range(len(chain) - 1):
                chain[i].next = chain[i+1]
            if chain:
                chain[-1].next = None

    def run(self):
        for _ in range(NUM_CLIENT_REQUESTS):
            # Simulate request
            request_time = self.env.now
            group = random.randint(0, NUM_REPLICA_GROUPS - 1)
            chain = self.chains[group]
            if chain:
                head = chain[0]
                tail = chain[-1]
                if not head.failed and not tail.failed:
                    latency = random.uniform(1, 10)
                    yield self.env.timeout(latency)
                    self.latency[request_time] = self.env.now - request_time
                    tail.requests_handled += 1
                    
                    # Simulate network overhead
                    network_overhead = random.uniform(0.1, 1.0)
                    self.total_network_overhead += network_overhead

            # Check for failures
            for node in self.nodes:
                if random.random() < 0.001:  # 0.1% chance of failure
                    node.failed = True
                elif node.failed and random.random() < 0.01:  # 1% chance of recovery
                    node.failed = False
            self.reconstruct()

# Simulation    
env = simpy.Environment()
nodes = [Node(i, i % NUM_REPLICA_GROUPS) for i in range(NUM_NODES)]
chain = ChainReplication(env, nodes)
env.run(until=NUM_CLIENT_REQUESTS)

# Calculate availability per replica group
# Calculate availability per replica group
availability_per_group = [
    sum(n.requests_handled for n in chain.chains[group]) / NUM_CLIENT_REQUESTS
    for group in range(NUM_REPLICA_GROUPS)
]

# Stats
total_latency = sum(chain.latency.values())
average_latency = total_latency / len(chain.latency) if chain.latency else 0
availability = sum(availability_per_group) / NUM_REPLICA_GROUPS
average_network_overhead = chain.total_network_overhead / NUM_CLIENT_REQUESTS

print(f"1. Average Latency: {average_latency:.3f} ms")
print(f"2. Availability: {availability* 100:.2%}")
print(f"3. Availability per Replica Group: {[f'{a:.2%}' for a in availability_per_group]}")
print(f"4. Average Network Overhead per Request: {average_network_overhead:.6f} MB")

