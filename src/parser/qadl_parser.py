class Qubit:
    def __init__(self, name):
        self.name = name

class QuantumGate:
    def __init__(self, name, qubits):
        self.name = name
        self.qubits = qubits

class Measurement:
    def __init__(self, qubit, classical_bit):
        self.qubit = qubit
        self.classical_bit = classical_bit

class Node:
    def __init__(self, name):
        self.name = name

class Edge:
    def __init__(self, name, source, destination, capacity, edge_type):
        self.name = name
        self.source = source
        self.destination = destination
        self.capacity = capacity
        self.edge_type = edge_type

class Flow:
    def __init__(self, source, destination, amount):
        self.source = source
        self.destination = destination
        self.amount = amount

class QuantumCircuitDef:
    def __init__(self, name):
        self.name = name
        self.qubits = []
        self.gates = []
        self.measurements = []
        self.classical_bits = {}
        self.nodes = []
        self.edges = []
        self.flows = []
        self.modules = {}  # Store module definitions

    def add_qubit(self, qubit):
        self.qubits.append(qubit)

    def add_gate(self, gate):
        self.gates.append(gate)

    def add_measurement(self, measurement):
        if measurement.classical_bit not in self.classical_bits:
            self.classical_bits[measurement.classical_bit] = len(self.classical_bits)
        self.measurements.append(measurement)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def add_flow(self, flow):
        self.flows.append(flow)

    def add_module(self, name, gates):
        self.modules[name] = gates

def parse_block(lines, line_number):
    block_lines = []
    while line_number < len(lines):
        line = lines[line_number].strip()
        if line == '}':
            break
        block_lines.append(line)
        line_number += 1
    return block_lines, line_number

def parse_qadl(script):
    lines = script.split('\n')
    circuit = None
    modules = {}  # Dictionary to store module definitions
    in_comment_block = False  # Track block comments
    parsing_started = False  # Track if we're inside @startqadl and @endqadl
    line_number = 0

    while line_number < len(lines):
        line = lines[line_number].strip()

        # Handle @startqadl and @endqadl
        if line == "@startqadl":
            parsing_started = True
            line_number += 1
            continue
        elif line == "@endqadl":
            parsing_started = False
            break

        if not parsing_started:
            line_number += 1
            continue

        # Skip empty lines
        if not line:
            line_number += 1
            continue

        # Handle inline comments
        if "//" in line:
            line = line.split("//", 1)[0].strip()

        # Handle block comments
        if line.startswith("/*"):
            in_comment_block = True
            line_number += 1
            continue
        if in_comment_block:
            if "*/" in line:
                in_comment_block = False
            line_number += 1
            continue

        # Parse Circuit Declaration
        if line.startswith("Circuit"):
            parts = line.split()
            if len(parts) != 3 or parts[2] != '{':
                raise SyntaxError(f"Syntax error on line {line_number + 1}: Invalid circuit declaration. Expected 'Circuit <name> {{'")
            circuit = QuantumCircuitDef(parts[1])
            line_number += 1
            continue

        elif line.startswith('qubit') and circuit:
            parts = line.split()
            if len(parts) != 2:
                raise SyntaxError(f"Syntax error on line {line_number + 1}: Invalid qubit declaration. Expected 'qubit <name>'")
            circuit.add_qubit(Qubit(parts[1]))

        elif line.startswith('gate') and circuit:
            parts = line.split()
            gate_name = parts[1]
            qubits = parts[2:]

            # Check if it's a module call
            if gate_name in modules:
                # Expand the module with actual qubits
                module_gates = modules[gate_name]
                if len(qubits) != len(module_gates[0].qubits):
                    raise ValueError(f"Module '{gate_name}' called with incorrect number of qubits.")
                for module_gate in module_gates:
                    expanded_qubits = [qubits[i] for i in range(len(module_gate.qubits))]
                    circuit.add_gate(QuantumGate(module_gate.name, expanded_qubits))
            else:
                circuit.add_gate(QuantumGate(gate_name, qubits))

        elif line.startswith('measure') and circuit:
            parts = line.split()
            if len(parts) != 4 or parts[2] != '->':
                raise SyntaxError(f"Syntax error on line {line_number + 1}: Invalid measurement declaration. Expected 'measure <qubit> -> <classical_bit>'")
            qubit = parts[1]
            classical_bit = parts[3]
            circuit.add_measurement(Measurement(qubit, classical_bit))

        elif line.startswith('module'):
            # Parse module definition
            parts = line.split()
            if len(parts) != 3 or parts[2] != '{':
                raise SyntaxError(f"Syntax error on line {line_number + 1}: Invalid module declaration. Expected 'module <name> {{'")
            module_name = parts[1]
            module_script, line_number = parse_block(lines, line_number + 1)
            sub_module_gates = parse_qadl('\n'.join(module_script)).gates  # Parse the module as a separate circuit
            modules[module_name] = sub_module_gates

        elif line.startswith('Node') and circuit:
            parts = line.split()
            if len(parts) != 2:
                raise SyntaxError(f"Syntax error on line {line_number + 1}: Invalid node declaration. Expected 'Node <name>'")
            circuit.add_node(Node(parts[1]))

        elif line.startswith('Edge') and circuit:
            parts = line.split()
            if len(parts) < 5 or parts[3] != '->':
                raise SyntaxError(f"Syntax error on line {line_number + 1}: Invalid edge declaration. Expected 'Edge <name> <from_node> -> <to_node> {{'")
            edge_name = parts[1]
            from_node = parts[2]
            to_node = parts[4].strip('{').strip()
            edge_type = None
            capacity = None
            block_lines, line_number = parse_block(lines, line_number + 1)
            for block_line in block_lines:
                block_parts = block_line.split()
                if block_parts[0] == "FlowType":
                    edge_type = block_parts[1].strip('"')
                elif block_parts[0] == "Capacity":
                    capacity = float(block_parts[1])
            circuit.add_edge(Edge(edge_name, from_node, to_node, capacity, edge_type))

        elif line.startswith('flow') and circuit:
            parts = line.split()
            if len(parts) != 5:
                raise SyntaxError(f"Syntax error on line {line_number + 1}: Invalid flow declaration. Expected 'flow <source> -> <destination> amount <amount>'")
            source = parts[1]
            destination = parts[3]
            amount = float(parts[4])
            circuit.add_flow(Flow(source, destination, amount))

        elif line.startswith('}'):
            line_number += 1
            continue

        else:
            raise SyntaxError(f"Syntax error on line {line_number + 1}: Unrecognized statement '{line}'.")

        line_number += 1

    if not circuit:
        raise SyntaxError("No valid circuit found in the script.")
    
    # Assign parsed modules to the main circuit definition
    if circuit:
        circuit.modules = modules
    return circuit

