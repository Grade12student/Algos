import random
import time

# Constants
NUM_NODES = 10
NUM_GROUPS = 3
NUM_OPERATIONS = 1000
FAILURE_RATE = 0.01
RECOVERY_RATE = 0.1

class Node:
    def __init__(self, id, group):
        self.id = id
        self.group = group
        self.successor = None
        self.predecessor = None
        self.failed = False
        self.data = {}

    def find_successor(self, key):
        if not self.failed:
            # Adjust the range check to correctly handle the wrap-around case
            if self.id < key <= self.successor.id or (self.id > self.successor.id and (key > self.id or key <= self.successor.id)):
                return self.successor
            else:
                return self.successor.find_successor(key)
        return None



class ChordRing:
    def __init__(self, num_nodes, num_groups):
        self.nodes = []
        for i in range(num_nodes):
            node = Node(i, f"Group{i % num_groups}")
            self.nodes.append(node)
        
        # Set up the ring
        for i in range(num_nodes):
            self.nodes[i].successor = self.nodes[(i + 1) % num_nodes]
            self.nodes[i].predecessor = self.nodes[(i - 1) % num_nodes]

        self.total_operations = 0
        self.successful_operations = 0
        self.total_latency = 0
        

    def put(self, key, value):
        if not self.nodes:
            return False
        
        start_node = random.choice(self.nodes)
        start_time = time.time()
        target_node = start_node.find_successor(key)
        
        if target_node and not target_node.failed:
            target_node.data[key] = value
            end_time = time.time()
            self.total_latency += (end_time - start_time) * 1000  # Convert to milliseconds
            return True
        return False

    def get(self, key):
        if not self.nodes:
            return None
        
        start_node = random.choice(self.nodes)
        start_time = time.time()
        target_node = start_node.find_successor(key)
        
        if target_node and not target_node.failed:
            value = target_node.data.get(key)
            end_time = time.time()
            self.total_latency += (end_time - start_time) * 1000  # Convert to milliseconds
            return value
        return None

    def run_simulation(self, num_operations):
        for _ in range(num_operations):
            self.total_operations += 1
            
            # Simulate node failures and recoveries
            for node in self.nodes:
                if not node.failed and random.random() < FAILURE_RATE:
                    node.failed = True
                elif node.failed and random.random() < RECOVERY_RATE:
                    node.failed = False
            
            # Perform operation
            if random.random() < 0.5:  # 50% chance of put operation
                key = random.randint(0, 1000)
                value = f"Value-{key}"
                if self.put(key, value):
                    self.successful_operations += 1
            else:  # 50% chance of get operation
                key = random.randint(0, 1000)
                if self.get(key) is not None:
                    self.successful_operations += 1

    def calculate_availability(self):
        if self.total_operations == 0:
            return 0
        return self.successful_operations / self.total_operations

    def calculate_availability_per_group(self):
        group_availability = {f"Group{i}": {"total": 0, "available": 0} for i in range(NUM_GROUPS)}
        for node in self.nodes:
            group_availability[node.group]["total"] += 1
            if not node.failed:
                group_availability[node.group]["available"] += 1
        
        return {group: data["available"] / data["total"] for group, data in group_availability.items()}

    def print_results(self):
        availability = self.calculate_availability()
        avg_latency = self.total_latency * 1000 / self.successful_operations if self.successful_operations > 0 else 0  # Convert to ms
        availability_per_group = self.calculate_availability_per_group()
        
        # Calculate network overhead
        total_data_size = sum(len(str(key) + str(value)) for node in self.nodes for key, value in node.data.items())
        avg_network_overhead = total_data_size / self.total_operations / (1024 * 1024) if self.total_operations > 0 else 0  # Convert to MB
        
        print(f"1. Average Latency: {avg_latency:.3f} ms")
        print(f"2. Overall Availability: {availability:.2%}")
        print(f"3. Availability per Group: {availability_per_group}")
        print(f"4. Average Network Overhead per Request: {avg_network_overhead:.6f} MB")
        print(f"Successful Operations: {self.successful_operations}")
        print(f"Total Operations: {self.total_operations}")

if __name__ == "__main__":
    chord_ring = ChordRing(NUM_NODES, NUM_GROUPS)
    chord_ring.run_simulation(NUM_OPERATIONS)
    chord_ring.print_results()


'''import random
import time

# Constants
NUM_NODES = 10
NUM_GROUPS = 3  # Number of groups
BITS = 160  # Number of bits for the Chord ring

class Storage:
    def __init__(self):
        self.data = {}

    def put(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

class Node:
    def __init__(self, id, group=None):
        self.id = id
        self.group = group  # Group identifier
        self.finger_table = {}
        self.successor = None
        self.predecessor = None
        self.failed = False
        self.ring = None

    def join(self, ring):
        self.ring = ring
        ring_nodes = ring.nodes
        if not ring_nodes:
            # First node in the ring is its own successor and predecessor
            self.successor = self
            self.predecessor = self
        else:
            # Find the predecessor in the ring for this node
            predecessor = ring.find_predecessor(self.id)
            self.successor = predecessor.successor
            predecessor.successor = self
            self.notify(predecessor)

        ring_nodes.append(self)

    def stabilize(self):
        if self.successor and not self.successor.failed:
            x = self.successor.predecessor
            if x and self.ring.in_interval(self.id, self.successor.id, x.id):
                self.successor = x
            self.successor.notify(self)

    def notify(self, n):
        if not self.predecessor or self.ring.in_interval(self.predecessor.id, self.id, n.id):
            self.predecessor = n

    def in_interval(self, a, b, x):
        # Handles wrap-around in the ring
        if a < b:
            return a < x <= b
        else:
            return a < x or x <= b

    def perform_operation(self):
        operation_time = random.uniform(0.1, 0.5)
        time.sleep(operation_time)
        self.send_data(random.randint(1, 100))

    def mark_failed(self):
        self.failed = True

    def send_data(self, data_size):
        if self.ring:
            self.ring.send_data(data_size)

class Ring:
    def __init__(self):
        self.nodes = []
        self.latency = []
        self.network_overhead = 0
        self.request_count = 0

    def stabilize(self):
        for node in self.nodes:
            if not node.failed:
                node.stabilize()

    def find_predecessor(self, id):
        # Find the predecessor node in the ring
        for node in self.nodes:
            if self.in_interval(node.id, node.successor.id, id):
                return node
        return None

    def in_interval(self, a, b, x):
        if a < b:
            return a < x <= b
        else:
            return a < x or x <= b

    def operation_start(self):
        self.operation_start_time = time.time()
        self.request_count += 1

    def operation_end(self):
        end_time = time.time()
        latency = end_time - self.operation_start_time
        self.latency.append(latency)

    def send_data(self, data_size):
        self.network_overhead += data_size

    def perform_operations(self, num_operations):
        for _ in range(num_operations):
            random_node = random.choice([n for n in self.nodes if not n.failed])
            self.operation_start()
            random_node.perform_operation()
            self.operation_end()

# Availability calculations
def calculate_availability(ring):
    total_nodes = len(ring.nodes)
    available_nodes = sum(1 for node in ring.nodes if not node.failed)
    availability = available_nodes / total_nodes
    return availability

def calculate_availability_per_group(ring):
    group_availability = {}
    for node in ring.nodes:
        group = node.group
        if group not in group_availability:
            group_availability[group] = {"total": 0, "available": 0}
        group_availability[group]["total"] += 1
        if not node.failed:
            group_availability[group]["available"] += 1

    availability_per_group = {
        group: group_data["available"] / group_data["total"] * 100 if group_data["total"] > 0 else 0
        for group, group_data in group_availability.items()
    }
    return availability_per_group

# Example usage
if __name__ == "__main__":
    ring = Ring()
    nodes = [
        Node(1, "GroupA"), Node(2, "GroupA"), Node(3, "GroupA"),
        Node(4, "GroupB"), Node(5, "GroupB"), Node(6, "GroupB"),
        Node(7, "GroupC"), Node(8, "GroupC"), Node(9, "GroupC"),
        Node(10, "GroupC")
    ]

    for node in nodes:
        node.join(ring)
        ring.stabilize()

    # Mark some nodes as failed for testing
    nodes[0].mark_failed()

    # Perform operations and calculate metrics
    ring.perform_operations(10)
    
    average_latency = sum(ring.latency) / len(ring.latency) if ring.latency else 0
    print(f"Average Latency: {average_latency:.3f} ms")

    availability = calculate_availability(ring)
    print(f"Availability: {availability:.3%}")

    availability_per_group = calculate_availability_per_group(ring)
    print(f"Availability per Group: {availability_per_group}")

    average_network_overhead = ring.network_overhead / len(ring.latency) / 1024
    print(f"Average Network Overhead per Request: {average_network_overhead:.3f} MB")
'''