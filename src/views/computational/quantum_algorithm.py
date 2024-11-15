class QuantumAlgorithm:
    def __init__(self, name):
        self.name = name
        self.steps = []

    def add_step(self, step):
        self.steps.append(step)

    def __repr__(self):
        return f"QuantumAlgorithm(name={self.name}, steps={self.steps})"
