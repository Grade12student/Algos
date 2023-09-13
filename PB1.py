import simpy
import random

# Constants
NUM_NODES = 9
NUM_REPLICA_GROUPS = 3
NUM_CLIENT_REQUESTS = 10000

class PrimaryBackup:
    def __init__(self, sim, node_id, replica_group):
        self.sim = sim
        self.node_id = node_id
        self.replica_group = replica_group
        self.replicas = []
        self.primary = False
        self.requests_handled = 0
        self.failed = False

        self.sim.env.process(self.replica_process())
        self.sim.env.process(self.primary_process())

    def replica_process(self):
        while True:
            if not self.failed:
                for replica in self.replicas:
                    if not replica.failed and replica != self.primary:
                        propagation_delay = random.uniform(0.1, 1.0)  # Model propagation delay
                        self.sim.total_network_overhead += propagation_delay
                        yield self.sim.env.timeout(propagation_delay)
            yield self.sim.env.timeout(1)

    def primary_process(self):
        while True:
            if not self.failed and self.primary:
                wait_time = random.expovariate(1/5)
                yield self.sim.env.timeout(wait_time)

                if random.random() < 0.8:
                    request_latency = random.uniform(1, 10)
                    request_start = int(self.sim.env.now)
                    yield self.sim.env.timeout(request_latency)
                    self.sim.total_latency[request_start] += self.sim.env.now - request_start
                    self.requests_handled += 1

            yield self.sim.env.timeout(random.uniform(0.5, 1.5))

    def set_replicas(self, nodes):
        self.replicas = [node for node in nodes if node.replica_group == self.replica_group and node != self]

class Simulator:
    def __init__(self, env):
        self.env = env
        self.nodes = []
        self.total_latency = [0] * (NUM_CLIENT_REQUESTS * 2)
        self.total_network_overhead = 0

        for i in range(NUM_NODES):
            replica_group = i % NUM_REPLICA_GROUPS
            node = PrimaryBackup(self, i, replica_group)
            self.nodes.append(node)

            # Elect initial primaries for each replica group
            if not any(n.primary for n in self.nodes if n.replica_group == replica_group):
                node.primary = True

            node.set_replicas(self.nodes)

    def run(self):
        for i in range(NUM_CLIENT_REQUESTS):
            client = random.choice(self.nodes)
            primaries = [n for n in client.replicas if n.primary]
            if primaries:
                primary = random.choice(primaries)
                request_latency = random.uniform(1, 10)
                request_start = int(self.env.now)
                yield self.env.timeout(request_latency)
                self.total_latency[request_start] += self.env.now - request_start

        for _ in range(NUM_CLIENT_REQUESTS):
            yield self.env.timeout(1)
            for node in self.nodes:
                if random.random() < 0.01:
                    if not node.failed:
                        node.failed = True
                        print(f"Node {node.node_id} failed at time {self.env.now}")
                elif node.failed:
                    node.failed = False
                    print(f"Node {node.node_id} recovered at time {self.env.now}")

# Initialize SimPy environment
env = simpy.Environment()

# Create and run simulator
sim = Simulator(env)
env.process(sim.run())
env.run(until=NUM_CLIENT_REQUESTS * 2)

# Calculate and print statistics
total_latency = sum(sim.total_latency)
average_latency = total_latency / NUM_CLIENT_REQUESTS
average_network_overhead = sim.total_network_overhead / (NUM_CLIENT_REQUESTS * 2)  # Note: Using total simulation time

# Calculate overall availability
overall_availability = sum(node.requests_handled > 0 for node in sim.nodes) / len(sim.nodes)

# Calculate availability per replica group
availability_per_group = [
    sum(node.requests_handled > 0 for node in sim.nodes if node.replica_group == group) / len(sim.nodes)
    for group in range(NUM_REPLICA_GROUPS)
]

# Print statistics
print(f"1. Average Latency: {average_latency:.2f} ms")
print(f"2. Overall Availability: {overall_availability:.2%}")
print(f"3. Availability per Replica Group: {availability_per_group}")
print(f"4. Average Network Overhead per Request: {average_network_overhead:.3f} MB")  # Note: Using total simulation time

