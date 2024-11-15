from .qubit import Qubit
from .quantum_gate import QuantumGate

class QuantumCircuit:
    def __init__(self, name: str):
        self.name = name
        self.gates = []

    def add_gate(self, gate: QuantumGate):
        self.gates.append(gate)

    def __repr__(self):
        return f"QuantumCircuit(name={self.name}, gates={self.gates})"
