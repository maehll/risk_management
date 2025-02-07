from typing import List, Dict, Optional
from datetime import datetime
from ..models.risk import Risk

class RiskManager:
    def __init__(self):
        self.risks = {}
        self.next_id = 1
        self.project_budget = None
    
    def set_project_budget(self, budget: float):
        """Setzt das Projektbudget"""
        if budget <= 0:
            raise ValueError("Budget muss positiv sein")
        self.project_budget = budget
        
    def get_project_budget(self) -> float:
        """Gibt das Projektbudget zurück"""
        if self.project_budget is None:
            raise ValueError("Projektbudget wurde noch nicht gesetzt")
        return self.project_budget
    
    def add_risk(self, name: str, description: str, probability: float, 
                 impact: float, reporting_level: str, risk_type: str) -> Risk:
        """Fügt ein neues Risiko hinzu"""
        risk = Risk(
            id=self.next_id,
            name=name,
            description=description,
            probability=probability,
            impact=impact,
            reporting_level=reporting_level,
            risk_type=risk_type
        )
        self.risks[self.next_id] = risk
        self.next_id += 1
        return risk
    
    def update_risk(self, risk_id: int, **kwargs) -> Risk:
        if risk_id not in self.risks:
            raise ValueError(f"Risiko mit ID {risk_id} nicht gefunden")
        
        risk = self.risks[risk_id]
        for key, value in kwargs.items():
            if hasattr(risk, key):
                setattr(risk, key, value)
        
        risk.updated_at = datetime.now()
        return risk
    
    def delete_risk(self, risk_id: int) -> None:
        if risk_id not in self.risks:
            raise ValueError(f"Risiko mit ID {risk_id} nicht gefunden")
        del self.risks[risk_id]
    
    def get_risk(self, risk_id: int) -> Optional[Risk]:
        return self.risks.get(risk_id)
    
    def get_all_risks(self) -> list:
        """Gibt alle Risiken zurück"""
        return list(self.risks.values())
    
    def get_risks_by_type(self, risk_type: str) -> List[Risk]:
        return [risk for risk in self.risks.values() 
                if risk.risk_type.lower() == risk_type.lower()]
    
    def get_risks_by_reporting_level(self, level: str) -> List[Risk]:
        return [risk for risk in self.risks.values() 
                if risk.reporting_level.lower() == level.lower()]
    
    def get_high_risks(self) -> List[Risk]:
        return [risk for risk in self.risks.values() 
                if risk.risk_level == "Hoch"]
    
    def get_risks_by_owner(self, owner: str) -> List[Risk]:
        return [risk for risk in self.risks.values() 
                if risk.owner.lower() == owner.lower()]
    
    def get_overdue_risks(self) -> List[Risk]:
        now = datetime.now()
        return [risk for risk in self.risks.values() 
                if risk.due_date and risk.due_date < now]