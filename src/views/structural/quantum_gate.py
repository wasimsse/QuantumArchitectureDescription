# views/structural/quantum_gate.py

from qiskit.circuit.library import HGate, CXGate, RXGate, RYGate, RZGate

class QuantumGate:
    def __init__(self, name, type, target_qubit, control_qubit=None, angle=None):
        self.name = name
        self.type = type
        self.target_qubit = target_qubit
        self.control_qubit = control_qubit
        self.angle = angle

    def get_qiskit_gate(self):
        # Returns the Qiskit gate instance based on type
        if self.type == "H":
            return HGate()
        elif self.type == "CNOT":
            return CXGate()
        elif self.type == "RX" and self.angle is not None:
            return RXGate(self.angle)
        elif self.type == "RY" and self.angle is not None:
            return RYGate(self.angle)
        elif self.type == "RZ" and self.angle is not None:
            return RZGate(self.angle)
        else:
            raise ValueError(f"Unsupported gate type: {self.type}")

    def __repr__(self):
        return (f"QuantumGate(name={self.name}, type={self.type}, "
                f"target_qubit={self.target_qubit}, control_qubit={self.control_qubit}, angle={self.angle})")
