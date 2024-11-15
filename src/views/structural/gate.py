class QuantumGate:
    def __init__(self, name: str, target_qubits: list):
        self.name = name
        self.target_qubits = target_qubits  # List of qubits this gate acts on

    def __repr__(self):
        targets = ", ".join(self.target_qubits)
        return f"QuantumGate(name={self.name}, targets=[{targets}])"
