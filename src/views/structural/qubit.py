# views/structural/qubit.py

from qiskit import QuantumRegister

class Qubit:
    def __init__(self, name):
        self.name = name
        self.quantum_register = QuantumRegister(1, name=self.name)

    def __repr__(self):
        return f"Qubit(name={self.name})"
