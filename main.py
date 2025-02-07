import tkinter as tk
from src.gui.risk_window import RiskManagementApp

def main():
    root = tk.Tk()
    app = RiskManagementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()