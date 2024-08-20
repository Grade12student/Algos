import random
import time

# Constants
NUM_NODES = 5
NUM_PROPOSALS = 100
FAILURE_RATE = 0.01
RECOVERY_RATE = 0.1

class Node:
    def __init__(self, id):
        self.id = id
        self.promised_id = -1
        self.accepted_id = -1
        self.accepted_value = None
        self.is_failed = False
        self.total_time = 0
        self.failed_time = 0
        self.last_update_time = time.time()

    def update_time(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        self.total_time += elapsed_time
        if self.is_failed:
            self.failed_time += elapsed_time
        self.last_update_time = current_time

    def receive_prepare(self, proposer_id):
        if self.is_failed:
            return None
        if proposer_id > self.promised_id:
            self.promised_id = proposer_id
            return (self.accepted_id, self.accepted_value)
        return None

    def receive_accept(self, proposer_id, value):
        if self.is_failed:
            return False
        if proposer_id >= self.promised_id:
            self.promised_id = proposer_id
            self.accepted_id = proposer_id
            self.accepted_value = value
            return True
        return False

class PaxosSystem:
    def __init__(self, num_nodes):
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.total_proposals = 0
        self.successful_proposals = 0
        self.total_latency = 0

    def propose(self, proposer_id, value):
        proposal_id = random.randint(1, 1000000)
        prepare_phase = self.prepare(proposer_id, proposal_id)
        if prepare_phase:
            return self.accept(proposer_id, proposal_id, value)
        return False

    def prepare(self, proposer_id, proposal_id):
        promises = 0
        highest_accepted_id = -1
        highest_accepted_value = None

        for node in self.nodes:
            response = node.receive_prepare(proposal_id)
            if response is not None:
                promises += 1
                accepted_id, accepted_value = response
                if accepted_id > highest_accepted_id:
                    highest_accepted_id = accepted_id
                    highest_accepted_value = accepted_value

        return promises > len(self.nodes) // 2

    def accept(self, proposer_id, proposal_id, value):
        accepts = 0
        start_time = time.time()

        for node in self.nodes:
            if node.receive_accept(proposal_id, value):
                accepts += 1

        if accepts > len(self.nodes) // 2:
            end_time = time.time()
            self.total_latency += end_time - start_time
            self.successful_proposals += 1
            return True
        return False

    def run_simulation(self, num_proposals):
        for _ in range(num_proposals):
            self.total_proposals += 1
            proposer_id = random.randint(0, len(self.nodes) - 1)
            value = f"Value-{random.randint(1, 1000)}"

            # Simulate node failures and recoveries
            for node in self.nodes:
                node.update_time()  # Update time before changing the node state
                if not node.is_failed and random.random() < FAILURE_RATE:
                    node.is_failed = True
                elif node.is_failed and random.random() < RECOVERY_RATE:
                    node.is_failed = False

            self.propose(proposer_id, value)

    def print_results(self):
        availability = self.successful_proposals / self.total_proposals if self.total_proposals > 0 else 0
        avg_latency = self.total_latency * 1000 / self.successful_proposals if self.successful_proposals > 0 else 0
        
        # Estimate network overhead (this is a simplification)
        avg_network_overhead = len(str(self.nodes[0].accepted_value)) * self.successful_proposals / self.total_proposals / (1024 * 1024)
        
        print(f"1. Average Latency: {avg_latency:.3f} ms")
        print(f"2. Overall Availability: {availability:.2%}")
        print(f"3. Average Network Overhead per Request: {avg_network_overhead:.6f} MB")
        print(f"Successful Proposals: {self.successful_proposals}")
        print(f"Total Proposals: {self.total_proposals}")

        for node in self.nodes:
            node.update_time()
            node_availability = (node.total_time - node.failed_time) / node.total_time if node.total_time > 0 else 0
            print(f"Node {node.id} Availability: {node_availability:.2%}")

if __name__ == "__main__":
    paxos_system = PaxosSystem(NUM_NODES)
    paxos_system.run_simulation(NUM_PROPOSALS)
    paxos_system.print_results()


'''from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor
import random
import time

# Constants
NUM_MESSAGES = 10
PREPARE = "PREPARE"
PROMISE = "PROMISE"

class Node:
    def __init__(self, rank, nodes, lock, queue, initial_latency=0, initial_network_overhead=0):
        self.rank = rank
        self.nodes = nodes
        self.lock = lock
        self.queue = queue
        self.latency = initial_latency
        self.network_overhead = initial_network_overhead
        self.failed = False
        self.accepted_round = -1
        self.accepted_value = None

    def run(self):
        for _ in range(random.randint(1, NUM_MESSAGES)):  # Send a random number of messages
            self.propose()

    def handle_messages(self):
        for _ in range(random.randint(1, NUM_MESSAGES)):  # Receive and handle a random number of messages
            if not self.failed:
                self.receive_messages()

    def propose(self):
        proposed_value = f"Value from Node {self.rank}"
        proposed_round = random.randint(1, 1000)

        for node in self.nodes:
            if node != self:
                self.send_prepare(node, proposed_round)

        accepted_count = 0
        start_time = time.time()
        for node in self.nodes:
            if node != self and node.accepted_round == proposed_round:
                accepted_count += 1

        if accepted_count >= (len(self.nodes) // 2) + 1:
            end_time = time.time()
            self.latency += end_time - start_time
            self.network_overhead += len(proposed_value.encode())
            print(f"Node {self.rank} reached consensus: {proposed_value}")

    def send_prepare(self, other_node, round):
        message = {
            "type": PREPARE,
            "round": round,
            "node_rank": self.rank,
        }
        with self.lock:
            self.queue.put((other_node, message))

    def receive_messages(self):
        try:
            with self.lock:
                message = self.queue.get(timeout=1)  # Simulate network delay
            self.handle_message(message)
        except Exception:
            pass  # Ignore timeouts or other exceptions

    def handle_message(self, message):
        if message["type"] == PREPARE:
            self.handle_prepare(message)

    def handle_prepare(self, message):
        if message["round"] > self.accepted_round:
            self.accepted_round = message["round"]
            self.accepted_value = None  # Clear the accepted value
            response = {
                "type": PROMISE,
                "round": self.accepted_round,
                "node_rank": self.rank,
                "accepted_value": self.accepted_value,
            }
            sender_rank = message["node_rank"]
            with self.lock:
                self.queue.put((self.nodes[sender_rank], response))


if __name__ == "__main__":
    manager = Manager()
    queue = manager.Queue()
    lock = manager.Lock()  # Use a Manager Lock

    N = 5  # Number of Paxos nodes
    nodes = []

    with ProcessPoolExecutor() as executor:
        for i in range(N):
            node = Node(i, nodes, lock, queue, initial_latency=random.uniform(0.1, 0.5), initial_network_overhead=100)
            nodes.append(node)

        futures = []
        for n in nodes:
            futures.append(executor.submit(n.run))
            futures.append(executor.submit(n.handle_messages))

        for f in futures:
            f.result()

    for node in nodes:
        avail = (NUM_MESSAGES - node.failed) / NUM_MESSAGES
        print(f"Node {node.rank} availability: {avail:.2%}")

    total_latency = sum(node.latency for node in nodes) / (NUM_MESSAGES * len(nodes))
    total_network_overhead = sum(node.network_overhead for node in nodes) / (NUM_MESSAGES * len(nodes))

    overall_availability = sum(1 for node in nodes if not node.failed) / len(nodes)
    print(f"Overall Availability: {overall_availability:.3%}")
    print(f"Total Average Latency: {total_latency:.3f} seconds")
    print(f"Total Average Network Overhead: {total_network_overhead} bytes")'''