from qiskit import QuantumCircuit
from qiskit.visualization import circuit_drawer
from qiskit.circuit.library import CRZGate
import numpy as np

def apply_inverse_qft(qc, qubits):
    """Apply the inverse Quantum Fourier Transform."""
    n = len(qubits)
    for qubit in range(n // 2):
        qc.swap(qubits[qubit], qubits[n - qubit - 1])
    for j in range(n):
        for m in range(j):
            qc.cp(-np.pi / float(2 ** (j - m)), qubits[j], qubits[m])
        qc.h(qubits[j])

def execute_network(circuit_def):
    # Logic to simulate the network flow, node behavior, etc.
    for node in circuit_def.nodes:
        print(f"Processing node: {node.name}")
        # Custom logic for node processing

    for edge in circuit_def.edges:
        print(f"Processing edge from {edge.source} to {edge.destination} with capacity {edge.capacity}")
        # Custom logic for edge processing

    for flow in circuit_def.flows:
        print(f"Processing flow from {flow.source} to {flow.destination} amount {flow.amount}")
        # Custom logic for flow processing

def execute_circuit(circuit_def):
    if circuit_def.nodes or circuit_def.edges or circuit_def.flows:
        execute_network(circuit_def)
        return circuit_def.name

    num_qubits = len(circuit_def.qubits)
    num_classical_bits = len(circuit_def.classical_bits)
    qc = QuantumCircuit(num_qubits, num_classical_bits)

    qubit_index = {qubit.name: idx for idx, qubit in enumerate(circuit_def.qubits)}
    classical_bit_index = circuit_def.classical_bits

    # Expand and execute all gates and modules in the correct sequence
    def execute_module(module_name, assigned_qubits):
        if module_name not in circuit_def.modules:
            raise ValueError(f"Module '{module_name}' is not defined in the circuit.")
        module_gates = circuit_def.modules[module_name]
        for gate in module_gates:
            expanded_qubits = [assigned_qubits[i] for i in range(len(gate.qubits))]
            add_gate_to_circuit(qc, gate, qubit_index, expanded_qubits)

    def add_gate_to_circuit(qc, gate, qubit_index, qubits=None):
        if not qubits:
            qubits = gate.qubits
        if gate.name == 'Hadamard':
            qc.h(qubit_index[qubits[0]])
        elif gate.name == 'CNOT':
            qc.cx(qubit_index[qubits[0]], qubit_index[qubits[1]])
        elif gate.name == 'CZ':
            qc.cz(qubit_index[qubits[0]], qubit_index[qubits[1]])
        elif gate.name == 'X':
            qc.x(qubit_index[qubits[0]])
        elif gate.name == 'CR':
            qc.append(CRZGate(0.5), [qubit_index[qubits[0]], qubit_index[qubits[1]]])
        elif gate.name == 'CR2':
            qc.append(CRZGate(1.0), [qubit_index[qubits[0]], qubit_index[qubits[1]]])
        elif gate.name == 'InverseQFT':
            apply_inverse_qft(qc, [qubit_index[q] for q in qubits])
        elif gate.name == 'CCNOT':
            qc.ccx(qubit_index[qubits[0]], qubit_index[qubits[1]], qubit_index[qubits[2]])
        elif gate.name == 'Oracle':
            pass
        elif gate.name == 'Diffuser':
            pass
        else:
            raise ValueError(f"Unsupported gate: {gate.name}")

    for gate in circuit_def.gates:
        if gate.name in circuit_def.modules:
            # If the gate is a module, execute the module with the provided qubits
            execute_module(gate.name, gate.qubits)
        else:
            add_gate_to_circuit(qc, gate, qubit_index)

    for measurement in circuit_def.measurements:
        qc.measure(qubit_index[measurement.qubit], classical_bit_index[measurement.classical_bit])

    # Handle the conditional operations manually
    if circuit_def.name == "QuantumTeleportation":
        with qc.if_test((classical_bit_index['c0'], 1)):
            qc.z(qubit_index['q2'])
        with qc.if_test((classical_bit_index['c1'], 1)):
            qc.x(qubit_index['q2'])

    # Draw the circuit
    qc.draw(output='mpl', filename='quantum_circuit.png')
    return circuit_def.name

# Debugging and improved error messages
def debug_circuit_parser(circuit_def):
    if circuit_def is None:
        print("Error: No circuit was found or initialized.")
    elif not circuit_def.qubits:
        print("Error: The circuit has no defined qubits.")
    elif not circuit_def.gates:
        print("Error: The circuit has no defined gates.")
    elif not circuit_def.measurements:
        print("Warning: The circuit has no measurement operations.")
    else:
        print(f"Circuit '{circuit_def.name}' has been successfully parsed with:")
        print(f"- {len(circuit_def.qubits)} qubits")
        print(f"- {len(circuit_def.gates)} gates")
        print(f"- {len(circuit_def.measurements)} measurements")

# Added function to handle visualization in a more dynamic way
def visualize_circuit(qc):
    """Generate a visual representation of the quantum circuit."""
    try:
        circuit_drawer(qc, output='mpl', filename='quantum_circuit.png')
        print("Circuit visualization saved as 'quantum_circuit.png'.")
    except Exception as e:
        print(f"Failed to generate circuit visualization: {e}")
