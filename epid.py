import simpy
import random

# Constants
NUM_NODES = 100
NUM_CLIENT_REQUESTS = 10000

class EpidemicReplication:
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.data = set()
        self.latency = []
        self.network_overhead = 0
        self.requests_handled = 0
        self.failed = False
        self.env.process(self.run())

    def run(self):
        while True:
            if not self.failed:
                # Handle client request
                if random.random() < 0.1:  # 10% chance of receiving a client request
                    start_time = self.env.now
                    latency = random.uniform(1, 10)
                    yield self.env.timeout(latency)
                    self.latency.append(self.env.now - start_time)
                    self.requests_handled += 1

                # Gossip with random node
                other_node = random.choice([n for n in nodes if n != self])
                network_overhead = random.uniform(0.1, 1.0)
                self.network_overhead += network_overhead
                yield self.env.timeout(network_overhead)

                # Simulate data exchange
                new_data = other_node.data - self.data
                self.data.update(new_data)

            # Simulate node failure/recovery
            if random.random() < 0.001:  # 0.1% chance of failure
                self.failed = True
            elif self.failed and random.random() < 0.01:  # 1% chance of recovery if failed
                self.failed = False

            yield self.env.timeout(1)  # Wait for 1 time unit before next cycle

# Simulation    
env = simpy.Environment()
nodes = [EpidemicReplication(env, i) for i in range(NUM_NODES)]
env.run(until=NUM_CLIENT_REQUESTS)

# Calculate statistics
total_latency = sum(sum(node.latency) for node in nodes)
total_requests = sum(node.requests_handled for node in nodes)
average_latency = total_latency / total_requests if total_requests > 0 else 0

total_network_overhead = sum(node.network_overhead for node in nodes)
average_network_overhead = total_network_overhead / NUM_CLIENT_REQUESTS

# Calculate availability
overall_availability = sum(1 for node in nodes if not node.failed) / NUM_NODES

# Calculate availability per node (as we don't have explicit groups in Epidemic Replication)
availability_per_node = [node.requests_handled / NUM_CLIENT_REQUESTS for node in nodes]

print(f"1. Average Latency: {average_latency:.3f} ms")
print(f"2. Overall Availability: {overall_availability:.2%}")
print(f"3. Availability per Node (first 10 nodes): {[f'{a:.2%}' for a in availability_per_node[:10]]}")
print(f"4. Average Network Overhead per Request: {average_network_overhead/100:.6f} MB")