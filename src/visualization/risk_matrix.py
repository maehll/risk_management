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
        """Erstellt die Power-Matrix"""
        # Figure mit quadratischem Aspektverhältnis erstellen
        fig = plt.figure(figsize=(10, 10))  # Quadratische Grundgröße
        ax = fig.add_subplot(111, aspect='equal')  # Erzwingt quadratisches Verhältnis
        
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
            
            # Berechne maximale Anzahl von Risiken pro Zeile
            max_risks_per_row = min(3, num_risks)  # Maximal 3 Risiken nebeneinander
            num_rows = (num_risks + max_risks_per_row - 1) // max_risks_per_row
            
            # Berechne Schriftgröße basierend auf verfügbarem Platz
            # Ein Quadrant ist 1x1 Einheiten groß
            base_fontsize = 12  # Basis-Schriftgröße
            fontsize = min(
                base_fontsize / num_rows,  # Vertikale Anpassung
                base_fontsize / max_risks_per_row  # Horizontale Anpassung
            )
            fontsize = max(12, min(28, fontsize))  # Begrenzen zwischen 6 und 14
            
            for idx, risk_id in enumerate(risk_ids):
                # Berechne Position in Reihen und Spalten
                row = idx // max_risks_per_row
                col = idx % max_risks_per_row
                
                # Berechne x und y Position mit Offset
                x_offset = col * (0.8 / max_risks_per_row)  # Horizontaler Abstand
                y_offset = row * (0.8 / num_rows)  # Vertikaler Abstand
                
                x_pos = impact_level + 0.1 + x_offset
                y_pos = prob_level + 0.1 + y_offset
                
                # Text-Box mit weißem Text auf rotem Grund und schwarzem Rahmen erstellen
                ax.text(x_pos, y_pos, risk_id,
                       va='center', ha='left',
                       fontsize=fontsize,
                       color='white',
                       bbox=dict(
                           facecolor='red',
                           edgecolor='black',  # Schwarzer Rahmen
                           linewidth=1,        # Rahmendicke
                           pad=2,              # Innenabstand
                           boxstyle='round,pad=0.3'  # Abgerundete Ecken
                       ))
        
        # Layout optimieren und Quadrat erzwingen
        plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
        
        if save_path:
            # Speichern mit festgelegter DPI für konsistente Größe
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.close()
        else:
            # Anzeigen mit erzwungenem quadratischem Layout
            plt.show(block=True)
        
        return fig, ax 