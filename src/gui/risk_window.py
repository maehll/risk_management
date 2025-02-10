import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from src.services.risk_manager import RiskManager
from src.visualization.risk_matrix import RiskMatrix
import json

class RiskManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Risiko Management System")
        self.risk_manager = RiskManager()
        self.risk_matrix = RiskMatrix()
        
        # Dropdown-Optionen
        self.reporting_levels = ["Project", "Program", "SteerCo"]
        self.risk_types = ["Project", "Business"]
        
        # Projektbudget beim Start abfragen
        self.get_project_budget()
        
        # Hauptfenster-Konfiguration
        self.root.geometry("1000x600")
        
        # GUI-Elemente erstellen
        self.create_menu()
        self.create_main_layout()
        
    def get_project_budget(self):
        """Fragt das Projektbudget beim Start ab"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Projektbudget")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Bitte geben Sie das Projektbudget (Mio. €) ein:").pack(pady=5)
        budget_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=budget_var)
        entry.pack(pady=5)
        
        def set_budget():
            try:
                budget = float(budget_var.get())
                if budget <= 0:
                    raise ValueError("Budget muss positiv sein")
                self.risk_manager.set_project_budget(budget)
                dialog.destroy()
            except ValueError as e:
                messagebox.showerror("Fehler", str(e))
        
        ttk.Button(dialog, text="OK", command=set_budget).pack(pady=5)
        self.root.wait_window(dialog)
        
    def create_menu(self):
        """Erstellt das Menü"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Projektbudget ändern", command=self.change_project_budget)
        file_menu.add_command(label="Speichern", command=self.save_data)
        file_menu.add_command(label="Laden", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        
        # Bearbeiten-Menü
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Bearbeiten", menu=edit_menu)
        edit_menu.add_command(label="Ausgewähltes Risiko bearbeiten", 
                            command=lambda: self.edit_risk(None))
        
    def create_main_layout(self):
        """Erstellt das Hauptlayout"""
        # Eingabeformular
        self.create_input_form()
        # Risiko-Liste
        self.create_risk_list()
        # Matrix-Button
        self.create_matrix_button()
        
        # Grid-Konfiguration
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def create_input_form(self):
        """Erstellt das Eingabeformular"""
        input_frame = ttk.LabelFrame(self.root, text="Neues Risiko", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Eingabefelder
        self.entries = {}
        
        # Normale Eingabefelder
        normal_fields = [
            "Name:", "Beschreibung:", "Wahrscheinlichkeit (%):", 
            "Auswirkung (Mio. €):"
        ]
        
        row = 0
        for field in normal_fields:
            ttk.Label(input_frame, text=field).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(input_frame, width=50)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            self.entries[field] = entry
            row += 1
        
        # Dropdown für Reporting Level
        ttk.Label(input_frame, text="Reporting Level:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        reporting_var = tk.StringVar(value=self.reporting_levels[0])  # Standardwert setzen
        reporting_dropdown = ttk.Combobox(input_frame, textvariable=reporting_var, values=self.reporting_levels, state="readonly")
        reporting_dropdown.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        self.entries["Reporting Level:"] = reporting_dropdown
        row += 1
        
        # Dropdown für Risiko-Typ
        ttk.Label(input_frame, text="Risiko-Typ:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        type_var = tk.StringVar(value=self.risk_types[0])  # Standardwert setzen
        type_dropdown = ttk.Combobox(input_frame, textvariable=type_var, values=self.risk_types, state="readonly")
        type_dropdown.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        self.entries["Risiko-Typ:"] = type_dropdown
        row += 1
        
        # Button zum Hinzufügen
        ttk.Button(input_frame, text="Risiko hinzufügen", command=self.add_risk).grid(
            row=row, column=0, columnspan=2, pady=10
        )
        
    def create_risk_list(self):
        """Erstellt die Risiko-Liste mit Kontextmenü"""
        list_frame = ttk.Frame(self.root)
        list_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Treeview für Risiken
        columns = ("ID", "Name", "Beschreibung", "Wahrscheinlichkeit", "Auswirkung", 
                  "Erwartungswert", "Reporting Level", "Risiko-Typ", "Risiko-Level")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Spaltenüberschriften und Sortierungsfunktion hinzufügen
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Treeview-Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Kontextmenü für Treeview
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Bearbeiten", 
                               command=lambda: self.edit_risk(None))
        
        def show_context_menu(event):
            if self.tree.selection():  # Nur wenn ein Item ausgewählt ist
                context_menu.post(event.x_root, event.y_root)
        
        # Bindings
        self.tree.bind("<Double-1>", self.edit_risk)  # Doppelklick
        self.tree.bind("<Button-3>", show_context_menu)  # Rechtsklick
            
        # Grid-Konfiguration für list_frame
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
    def create_matrix_button(self):
        """Erstellt den Matrix-Button"""
        ttk.Button(self.root, text="Powermatrix anzeigen", 
                  command=self.show_power_matrix).grid(row=2, column=0, pady=10)
    
    def show_power_matrix(self):
        """Zeigt die Risiko-Matrix an"""
        risks = self.risk_manager.get_all_risks()
        project_budget = self.risk_manager.get_project_budget()
        self.risk_matrix.create_matrix(risks, project_budget, title="Risiko Matrix")

    def add_risk(self):
        """Fügt ein neues Risiko hinzu"""
        try:
            # Sammle Daten aus den Eingabefeldern
            name = self.entries['Name:'].get()
            description = self.entries['Beschreibung:'].get()
            probability = float(self.entries['Wahrscheinlichkeit (%):'].get())
            impact = float(self.entries['Auswirkung (Mio. €):'].get())
            reporting_level = self.entries['Reporting Level:'].get()
            risk_type = self.entries['Risiko-Typ:'].get()
            
            # Validierung
            if not name or not description:
                raise ValueError("Name und Beschreibung sind erforderlich")
            if not 0 <= probability <= 100:
                raise ValueError("Wahrscheinlichkeit muss zwischen 0 und 100 Prozent liegen")
            if impact < 0:
                raise ValueError("Auswirkung muss positiv sein")
            
            # Risiko hinzufügen
            risk = self.risk_manager.add_risk(
                name=name,
                description=description,
                probability=probability,
                impact=impact,
                reporting_level=reporting_level,
                risk_type=risk_type
            )
            
            # Erwartungswert berechnen
            expected_value = (probability * impact) / 100  # Wahrscheinlichkeit ist in Prozent
            
            # Aktualisiere Tabelle
            self.tree.insert('', 'end', values=(
                f"R-{risk.id}",  # Prefix "R-" hinzugefügt
                risk.name,
                risk.description,
                f"{risk.probability:.1f}",
                f"{risk.impact:.2f}",
                f"{expected_value:.2f}",
                risk.reporting_level,
                risk.risk_type,
                risk.risk_level
            ))
            
            # Felder leeren
            for entry in self.entries.values():
                entry.delete(0, 'end')
                
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))
            
    def clear_form(self):
        for entry in self.entries.values():
            if isinstance(entry, ttk.Combobox):
                entry.set('')  # Für Comboboxen
            else:
                entry.delete(0, tk.END)  # Für normale Eingabefelder
    
    def show_risk_details(self, risk):
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Details: {risk.name}")
        details_window.geometry("400x300")
        
        # Details anzeigen
        ttk.Label(details_window, text=f"ID: {risk.id}").pack(pady=5)
        ttk.Label(details_window, text=f"Name: {risk.name}").pack(pady=5)
        ttk.Label(details_window, text=f"Beschreibung: {risk.description}").pack(pady=5)
        ttk.Label(details_window, text=f"Budget: {risk.budget:.2f} Mio. €").pack(pady=5)
        ttk.Label(details_window, text=f"Wahrscheinlichkeit: {risk.probability:.1f}%").pack(pady=5)
        ttk.Label(details_window, text=f"Auswirkung: {risk.impact:.2f} Mio. €").pack(pady=5)
        ttk.Label(details_window, text=f"Reporting Level: {risk.reporting_level}").pack(pady=5)
        ttk.Label(details_window, text=f"Risiko-Typ: {risk.risk_type}").pack(pady=5)
        ttk.Label(details_window, text=f"Risk-Level: {risk.risk_level}").pack(pady=5)
    
    def save_data(self):
        """Speichert alle Risiken in eine JSON-Datei mit Dateiauswahl"""
        try:
            # Dateiauswahl-Dialog öffnen
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")],
                title="Risiken speichern unter"
            )
            
            if not filepath:  # Wenn Benutzer abbricht
                return
            
            risks_data = []
            for risk in self.risk_manager.risks.values():
                risks_data.append({
                    'id': risk.id,
                    'name': risk.name,
                    'description': risk.description,
                    'probability': risk.probability,
                    'impact': risk.impact,
                    'reporting_level': risk.reporting_level,
                    'risk_type': risk.risk_type
                })
            
            data = {
                'project_budget': self.risk_manager.get_project_budget(),
                'risks': risks_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            messagebox.showinfo("Erfolg", "Daten wurden erfolgreich gespeichert")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")

    def load_data(self):
        """Lädt Risiken aus einer JSON-Datei mit Dateiauswahl"""
        try:
            # Dateiauswahl-Dialog öffnen
            filepath = filedialog.askopenfilename(
                filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")],
                title="Risiken laden"
            )
            
            if not filepath:  # Wenn Benutzer abbricht
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Projektbudget setzen
            self.risk_manager.set_project_budget(data['project_budget'])
            
            # Bestehende Risiken löschen
            self.risk_manager.risks.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Neue Risiken laden
            for risk_data in data['risks']:
                risk = self.risk_manager.add_risk(
                    name=risk_data['name'],
                    description=risk_data['description'],
                    probability=risk_data['probability'],
                    impact=risk_data['impact'],
                    reporting_level=risk_data['reporting_level'],
                    risk_type=risk_data['risk_type']
                )
                
                # Erwartungswert berechnen
                expected_value = (risk.probability * risk.impact) / 100
                
                # Risiko zur Tabelle hinzufügen
                self.tree.insert('', 'end', values=(
                    f"R-{risk.id}",  # Prefix "R-" hinzugefügt
                    risk.name,
                    risk.description,
                    f"{risk.probability:.1f}",
                    f"{risk.impact:.2f}",
                    f"{expected_value:.2f}",
                    risk.reporting_level,
                    risk.risk_type,
                    risk.risk_level
                ))
            
            messagebox.showinfo("Erfolg", "Daten wurden erfolgreich geladen")
        except FileNotFoundError:
            messagebox.showwarning("Warnung", "Datei nicht gefunden")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden: {str(e)}")

    def on_risk_select(self, event):
        try:
            selected_item = self.tree.selection()[0]
            risk_id = int(self.tree.item(selected_item)['values'][0].replace('R-', ''))
            risk = self.risk_manager.get_risk(risk_id)
            if risk:
                self.show_risk_details(risk)
        except IndexError:
            pass  # Nichts ausgewählt
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))

    def edit_risk(self, event):
        """Öffnet Dialog zum Bearbeiten eines Risikos"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Risiko aus")
            return
            
        item = selection[0]
        risk_id = int(self.tree.item(item)['values'][0].replace('R-', ''))  # "R-" Prefix entfernen
        risk = self.risk_manager.risks[risk_id]
        
        # Dialog erstellen
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Risiko {risk_id} bearbeiten")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Eingabefelder
        entries = {}
        row = 0
        
        # Normale Eingabefelder
        normal_fields = [
            ("Name:", risk.name),
            ("Beschreibung:", risk.description),
            ("Wahrscheinlichkeit (%):", str(risk.probability)),
            ("Auswirkung (Mio. €):", str(risk.impact))
        ]
        
        for field, value in normal_fields:
            ttk.Label(dialog, text=field).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(dialog, width=50)
            entry.insert(0, value)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
            entries[field] = entry
            row += 1
        
        # Dropdown für Reporting Level
        ttk.Label(dialog, text="Reporting Level:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        reporting_var = tk.StringVar(value=risk.reporting_level)
        reporting_dropdown = ttk.Combobox(dialog, textvariable=reporting_var, values=self.reporting_levels, state="readonly")
        reporting_dropdown.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        entries["Reporting Level:"] = reporting_dropdown
        row += 1
        
        # Dropdown für Risiko-Typ
        ttk.Label(dialog, text="Risiko-Typ:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        type_var = tk.StringVar(value=risk.risk_type)
        type_dropdown = ttk.Combobox(dialog, textvariable=type_var, values=self.risk_types, state="readonly")
        type_dropdown.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        entries["Risiko-Typ:"] = type_dropdown
        row += 1
        
        def update():
            try:
                # Daten sammeln
                name = entries["Name:"].get()
                description = entries["Beschreibung:"].get()
                probability = float(entries["Wahrscheinlichkeit (%):"].get())
                impact = float(entries["Auswirkung (Mio. €):"].get())
                reporting_level = entries["Reporting Level:"].get()
                risk_type = entries["Risiko-Typ:"].get()
                
                # Validierung
                if not name or not description:
                    raise ValueError("Name und Beschreibung sind erforderlich")
                if not 0 <= probability <= 100:
                    raise ValueError("Wahrscheinlichkeit muss zwischen 0 und 100 Prozent liegen")
                if impact < 0:
                    raise ValueError("Auswirkung muss positiv sein")
                
                # Risiko aktualisieren
                risk.name = name
                risk.description = description
                risk.probability = probability
                risk.impact = impact
                risk.reporting_level = reporting_level
                risk.risk_type = risk_type
                risk._risk_level = risk._calculate_risk_level()
                
                # Erwartungswert berechnen
                expected_value = (probability * impact) / 100  # Wahrscheinlichkeit ist in Prozent
                
                # Treeview aktualisieren
                self.tree.item(item, values=(
                    f"R-{risk.id}",  # Prefix "R-" hinzugefügt
                    risk.name,
                    risk.description,
                    f"{risk.probability:.1f}",
                    f"{risk.impact:.2f}",
                    f"{expected_value:.2f}",
                    risk.reporting_level,
                    risk.risk_type,
                    risk.risk_level
                ))
                
                dialog.destroy()
                messagebox.showinfo("Erfolg", "Risiko wurde aktualisiert")
                
            except ValueError as e:
                messagebox.showerror("Fehler", str(e))
        
        # Update-Button
        ttk.Button(dialog, text="Aktualisieren", command=update).grid(
            row=row, column=0, columnspan=2, pady=10
        )

    def change_project_budget(self):
        """Öffnet Dialog zum Ändern des Projektbudgets"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Projektbudget ändern")
        dialog.geometry("300x120")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Aktuelles Budget anzeigen
        current_budget = self.risk_manager.get_project_budget()
        ttk.Label(dialog, text=f"Aktuelles Budget: {current_budget} Mio. €").pack(pady=5)
        
        ttk.Label(dialog, text="Neues Projektbudget (Mio. €):").pack(pady=5)
        budget_var = tk.StringVar(value=str(current_budget))
        entry = ttk.Entry(dialog, textvariable=budget_var)
        entry.pack(pady=5)
        
        def update_budget():
            try:
                budget = float(budget_var.get())
                if budget <= 0:
                    raise ValueError("Budget muss positiv sein")
                self.risk_manager.set_project_budget(budget)
                dialog.destroy()
                messagebox.showinfo("Erfolg", "Projektbudget wurde aktualisiert")
            except ValueError as e:
                messagebox.showerror("Fehler", str(e))
        
        ttk.Button(dialog, text="Aktualisieren", command=update_budget).pack(pady=10)

    def sort_treeview(self, col):
        """Sortiert die Treeview-Spalte auf- oder absteigend"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        if hasattr(self, '_last_sort_col') and self._last_sort_col == col:
            items.reverse()
            self._last_sort_col = None
        else:
            if col == "ID":  # Spezielle Behandlung für ID-Spalte mit "R-" Prefix
                items.sort(key=lambda x: int(x[0].replace('R-', '')))
            elif col in ["Wahrscheinlichkeit", "Auswirkung", "Erwartungswert"]:
                items.sort(key=lambda x: float(x[0]) if x[0] else 0)
            else:
                items.sort(key=lambda x: x[0].lower())
            self._last_sort_col = col
        
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)

    def update_power_matrix(self):
        """Aktualisiert die Power-Matrix"""
        # Matrix leeren
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        
        # Matrix neu aufbauen
        for i in range(11):
            for j in range(11):
                cell = tk.Frame(self.matrix_frame, width=40, height=40, 
                              bg=self.get_cell_color(10-i, j))
                cell.grid(row=i, column=j)
                cell.grid_propagate(False)
                
                # Risiken für diese Zelle finden
                risks_in_cell = []
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    prob = float(values[3])  # Wahrscheinlichkeit
                    impact = float(values[4])  # Auswirkung
                    
                    # Prüfen ob Risiko in diese Zelle gehört
                    if (prob // 10 == j and impact // 10 == 10-i):
                        risks_in_cell.append(f"R-{values[0]}")  # ID mit "R-" Präfix
                
                # Risiko-IDs in der Zelle anzeigen
                if risks_in_cell:
                    label = tk.Label(cell, text="\n".join(risks_in_cell),
                                   bg='red', fg='white',  # Weiße Schrift auf rotem Grund
                                   font=('Arial', 8))
                    label.place(relx=0.5, rely=0.5, anchor='center')

def main():
    root = tk.Tk()
    app = RiskManagementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()