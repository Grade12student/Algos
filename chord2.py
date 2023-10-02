import random
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
        self.successor = None  # Initialize successor as None
        self.failed = False  # Add a 'failed' attribute and initialize it as False
        self.ring = None  # Reference to the ring

    def join(self, ring):
        self.ring = ring  # Set the reference to the ring
        ring_nodes = ring.nodes
        if not ring_nodes:
            # If the ring is empty, set the first node as its own successor
            self.successor = self
        else:
            # Find the predecessor in the ring
            predecessor = None
            for node in ring_nodes:
                if ring.in_interval(node.id, node.successor.id, self.id):
                    predecessor = node
                    break

            if predecessor:
                # Set the successor as the current node's successor
                if predecessor.successor:
                    self.successor = predecessor.successor
                # Notify the predecessor to update its successor to the current node
                predecessor.notify(self)

        ring_nodes.append(self)  # Add the node to the ring

    def stabilize(self):
        if self.successor:
            # Update finger table entries and perform other stabilization tasks
            pass

    def closest_preceding_finger(self, id):
        if not self.finger_table:
            return None  # No preceding fingers
        for i in range(max(self.finger_table), -1, -1):
            if self.finger_table[i] and self.in_interval(self.id, self.finger_table[i].id, id):
                return self.finger_table[i]
        return None

    def notify(self, node):
        if self.in_interval(node.id, self.id, self.successor.id):
            self.successor = node

    def in_interval(self, a, b, x):
        if self.ring and self.successor:
            return (a < x <= b)
        else:
            return False

    def perform_operation(self):
        # Simulate an operation (e.g., lookup or data transfer)
        # For demonstration, we'll add a random delay to simulate the operation time
        operation_time = random.uniform(0.1, 0.5)  # Adjust the range as needed
        time.sleep(operation_time)  # Simulate the operation duration
        self.send_data(random.randint(1, 100))  # Simulate network overhead

    def mark_failed(self):
        self.failed = True

    def send_data(self, data_size):
        if self.ring:
            self.ring.send_data(data_size)

class Ring:
    def __init__(self):
        self.nodes = []
        self.latency = []  # To track latency of operations
        self.network_overhead = 0  # To track network overhead
        self.request_count = 0  # To count the number of requests

    def stabilize(self):
        for node in self.nodes:
            node.stabilize()

    def find_successor(self, id):
        for node in self.nodes:
            if self.in_interval(node.id, node.successor.id, id):
                return node.successor
        return None

    def in_interval(self, a, b, x):
        if self.nodes and self.nodes[0].successor:
            return (a < x <= b)
        else:
            return False

    def operation_start(self):
        self.operation_start_time = time.time()
        self.request_count += 1  # Increment request count

    def operation_end(self):
        end_time = time.time()
        latency = end_time - self.operation_start_time
        self.latency.append(latency)

    def send_data(self, data_size):
        self.network_overhead += data_size

    def perform_operations(self, num_operations):
        for _ in range(num_operations):
            random_node = random.choice(self.nodes)
            self.operation_start()
            random_node.perform_operation()
            self.operation_end()

# Calculate availability
def calculate_availability(ring):
    total_nodes = len(ring.nodes)
    available_nodes = sum(1 for node in ring.nodes if not node.failed)
    availability = available_nodes / total_nodes
    return availability

# Calculate availability per group
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
    node1 = Node(1, group="GroupA")
    node2 = Node(2, group="GroupA")
    node3 = Node(3, group="GroupA")
    node4 = Node(4, group="GroupB")
    node5 = Node(5, group="GroupB")
    node6 = Node(6, group="GroupB")
    node7 = Node(7, group="GroupC")
    node8 = Node(8, group="GroupC")
    node9 = Node(9, group="GroupC")
    node10 = Node(10, group="GroupC")


    # Join node1 first and let it stabilize
    node1.join(ring)
    ring.stabilize()  # Perform stabilization for node1
    node1.successor = node1  # Initialize successor

    # Now add node2 to the ring
    node2.join(ring)
    ring.stabilize()
    node2.successor = node1  # Initialize successor
    
    node3.join(ring)
    ring.stabilize()
    node3.successor = node1  # Initialize successor
    
    node4.join(ring)
    node4.successor = node1  # Initialize successor
    
    node5.join(ring)
    node5.successor = node1  # Initialize successor
    node6.join(ring)
    node6.successor = node1  # Initialize successor

    node7.join(ring)
    node7.successor = node1  # Initialize successor
    node8.join(ring)
    node8.successor = node1  # Initialize successor
    node9.join(ring)
    node9.successor = node1  # Initialize successor
    node10.join(ring)
    node10.successor = node1  # Initialize successor

    # Mark some nodes as failed for testing (simulate failures)
    node1.failed = True

    # Simulate operations and calculate metrics
    ring.perform_operations(10)  # Simulate 10 operations

    # Calculate and print metrics
    average_latency = sum(ring.latency) / len(ring.latency) if ring.latency else 0
    print(f"Average Latency: {average_latency:.3f} ms")
    
    availability = calculate_availability(ring)
    print(f"Availability: {availability:.3%}")

    availability_per_group = calculate_availability_per_group(ring)
    print(f"Availability per Replica Group: {availability_per_group}")

    average_network_overhead = ring.network_overhead / len(ring.latency) / 1024   # Convert bytes to MB
    print(f"Average Network Overhead per Request: {average_network_overhead:.3f} MB")
