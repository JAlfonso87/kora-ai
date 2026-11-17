from dataclasses import dataclass

@dataclass
class HypothesisPosterior:
    id: str
    label: str
    probability: float
    prior: float
