# views/structural/quantum_circuit.py

from qiskit import QuantumCircuit

class QuantumCircuitWrapper:
    def __init__(self, name, num_qubits):
        self.name = name
        self.num_qubits = num_qubits
        self.circuit = QuantumCircuit(num_qubits)

    def add_gate(self, gate):
        # Adds a Qiskit gate to the circuit
        if gate.type == "H":
            self.circuit.h(gate.target_qubit)
        elif gate.type == "CNOT":
            self.circuit.cx(gate.control_qubit, gate.target_qubit)
        elif gate.type == "RX" and gate.angle is not None:
            self.circuit.rx(gate.angle, gate.target_qubit)
        elif gate.type == "RY" and gate.angle is not None:
            self.circuit.ry(gate.angle, gate.target_qubit)
        elif gate.type == "RZ" and gate.angle is not None:
            self.circuit.rz(gate.angle, gate.target_qubit)
        else:
            raise ValueError(f"Unsupported gate type: {gate.type}")

    def __repr__(self):
        return f"QuantumCircuitWrapper(name={self.name}, circuit={self.circuit})"
