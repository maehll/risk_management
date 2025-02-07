from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Risk:
    id: int
    budget: float      # Budget in Mio. Euro
    name: str
    description: str
    probability: float  # 0-100 (Prozent)
    impact: float      # Auswirkung in Mio. Euro
    reporting_level: str  # Niedrig, Mittel, Hoch
    risk_type: str      # Operationell, Strategisch, Finanziell, Extern
    created_at: datetime
    updated_at: datetime
    
    @property
    def risk_score(self) -> float:
        # Wahrscheinlichkeit wird von Prozent in Dezimal umgerechnet
        return (self.probability / 100) * self.impact
    
    @property
    def risk_level(self) -> str:
        return self._risk_level
    
    @property
    def budget_usage_percent(self) -> float:
        return (self.impact / self.budget * 100) if self.budget > 0 else 0
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'budget': self.budget,
            'name': self.name,
            'description': self.description,
            'probability': self.probability,
            'impact': self.impact,
            'reporting_level': self.reporting_level,
            'risk_type': self.risk_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'budget_usage_percent': self.budget_usage_percent
        }

    def __init__(self, id: int, name: str, description: str, probability: float, 
                 impact: float, reporting_level: str, risk_type: str):
        self.id = id
        self.name = name
        self.description = description
        self.probability = probability
        self.impact = impact
        self.reporting_level = reporting_level
        self.risk_type = risk_type
        self._risk_level = self._calculate_risk_level()

    def _calculate_risk_level(self) -> str:
        risk_value = self.probability * self.impact
        if risk_value < 10:
            return "Niedrig"
        elif risk_value < 30:
            return "Mittel"
        else:
            return "Hoch"