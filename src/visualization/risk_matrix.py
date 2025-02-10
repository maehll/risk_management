import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict
from src.models.risk import Risk

class RiskMatrix:
    def __init__(self):
        self.levels = ["very low", "low", "medium", "high", "very high"]
        
    def _map_impact_to_level(self, impact: float, budget: float) -> int:
        """Mappt Impact-Werte auf Matrix-Level (0-4) basierend auf dem Projektbudget"""
        impact_percentage = (impact / budget) * 100
        if impact_percentage <= 5:
            return 0  # very low
        elif impact_percentage <= 10:
            return 1  # low
        elif impact_percentage <= 50:
            return 2  # medium
        elif impact_percentage <= 75:
            return 3  # high
        else:
            return 4  # very high
    
    def _map_probability_to_level(self, probability: float) -> int:
        """Mappt Wahrscheinlichkeits-Werte auf Matrix-Level (0-4)"""
        if probability <= 5:
            return 0  # very low
        elif probability <= 10:
            return 1  # low
        elif probability <= 50:
            return 2  # medium
        elif probability <= 75:
            return 3  # high
        else:
            return 4  # very high
    
    def _group_risks_by_position(self, risks: List[Risk], project_budget: float) -> Dict[Tuple[int, int], List[str]]:
        """Gruppiert Risiken nach ihrer Position in der Matrix"""
        positions = defaultdict(list)
        for risk in risks:
            impact_level = self._map_impact_to_level(risk.impact, project_budget)
            prob_level = self._map_probability_to_level(risk.probability)
            positions[(impact_level, prob_level)].append(f"R-{risk.id}")  # Statt risk.name nun R-{risk.id}
        return positions
    
    def _truncate_text(self, text: str, max_chars: int = 20) -> str:
        """Kürzt Text auf maximale Zeichenanzahl"""
        if len(text) <= max_chars:
            return text
        return text[:max_chars-3] + "..."
            
    def create_matrix(self, risks: List[Risk], project_budget: float, title: str = "Risiko Matrix", save_path: str = None):
        # Figure und Axes erstellen
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Titel setzen
        plt.title(title, pad=20, fontsize=14, fontweight='bold')
        
        # Matrix für die Farbfelder erstellen (5x5)
        matrix = np.zeros((5, 5))
        for i in range(5):
            for j in range(5):
                if i + j <= 2:
                    matrix[i, j] = 1  # Grün
                elif i + j >= 6:
                    matrix[i, j] = 3  # Rot
                else:
                    matrix[i, j] = 2  # Gelb
        
        # Farbpalette definieren
        colors = ['#90EE90', '#FFFF00', '#FF6B6B']  # Grün, Gelb, Rot
        cmap = plt.cm.colors.ListedColormap(colors)
        
        # Farbige Matrix zeichnen
        ax.pcolormesh(np.arange(6), np.arange(6), matrix, cmap=cmap)
        
        # Gitternetz bei ganzzahligen Werten
        ax.grid(True, color='black', linewidth=1)
        ax.set_xticks(range(6))
        ax.set_yticks(range(6))
        
        # Achsenbeschriftungen
        ax.set_xlabel('Impact', fontsize=12, fontweight='bold', labelpad=20)
        ax.set_ylabel('Probability', fontsize=12, fontweight='bold', labelpad=45)
        
        # Beschriftungen direkt an den Achsen hinzufügen
        for i in range(5):
            # X-Achsen-Beschriftungen
            ax.text(i + 0.5, -0.05, self.levels[i], 
                   ha='center', va='top')
            # Y-Achsen-Beschriftungen
            ax.text(-0.05, i + 0.5, self.levels[i], 
                   ha='right', va='center')
        
        # Numerische Beschriftungen ausblenden
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        # Achsengrenzen setzen
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)
        
        # Risiken nach Position gruppieren
        positions = self._group_risks_by_position(risks, project_budget)
        
        # Risiken platzieren
        for (impact_level, prob_level), risk_ids in positions.items():
            num_risks = len(risk_ids)
            # Berechne gleichmäßige Abstände innerhalb des Quadranten
            spacing = 0.8 / max(num_risks, 1)  # 0.8 um etwas Rand zu lassen
            
            for idx, risk_id in enumerate(risk_ids):
                # Berechne y-Position mit Offset
                y_pos = prob_level + 0.1 + (idx * spacing)
                
                # Text-Box mit weißem Text auf rotem Grund erstellen
                ax.text(impact_level + 0.05, y_pos, risk_id,
                       va='center', ha='left', fontsize=8,
                       color='white',  # Weiße Schrift
                       bbox=dict(facecolor='red', edgecolor='none', pad=2))  # Roter Hintergrund
        
        # Layout optimieren
        plt.tight_layout()
        
        # Plot anzeigen
        plt.show() 