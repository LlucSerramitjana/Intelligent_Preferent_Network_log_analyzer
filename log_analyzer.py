import pandas as pd
import re
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Función principal de parseo ---
def parse_logs(input_file, output_folder):
    VALID_ACTIONS = ['UNEXPECTED_DATA_VALUE', 'DIAMETER_UNABLE_TO_COMPLY', 'RELAY']
    rows = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                parts = line.split('] ', 1)[1].split(';')
            except IndexError:
                continue

            imsi = parts[6] if len(parts) > 6 else ''
            timestamp = parts[12] if len(parts) > 12 else ''
            operator = parts[17] if len(parts) > 17 else ''
            country = parts[9] if len(parts) > 9 else ''

            # Determinar description
            if len(parts) > 35 and parts[35] in ['LTE', 'GSM', 'GPRS']:
                description = parts[35]
            else:
                description = parts[30] if len(parts) > 30 else ''

            # Determinar action
            action_candidates = []
            for idx in [18, 19, 34]:
                if len(parts) > idx and parts[idx] in VALID_ACTIONS:
                    action_candidates.append(parts[idx])
            action = action_candidates[0] if action_candidates else ''

            # Extraer IPNLogic y PNLogic
            ipn_logic_match = re.search(r'IPNLogic:\s*([^;]+)', line)
            pn_logic_match = re.search(r'PNLogic:\s*([^;]+)', line)

            logic_values = []
            if ipn_logic_match:
                logic_values.append(ipn_logic_match.group(1).strip())
            if pn_logic_match:
                logic_values.append(pn_logic_match.group(1).strip())

            ipn_logic = ', '.join(logic_values) if logic_values else ''

            rows.append({
                'IMSI': imsi,
                'Timestamp': timestamp,
                'Operator': operator,
                'Country': country,
                'Action': action,
                'Description': description,
                'IPNLogic': ipn_logic
            })

    # Crear DataFrame
    FIELDS = ['IMSI', 'Timestamp', 'Operator', 'Country', 'Action', 'Description', 'IPNLogic']
    df = pd.DataFrame(rows, columns=FIELDS)

    # --- Lógica para versiones infinitas ---
    base_name = os.path.join(output_folder, 'steering_events.xlsx')
    counter = 0
    final_name = base_name

    while os.path.exists(final_name):
        counter += 1
        final_name = os.path.join(output_folder, f"steering_events({counter}).xlsx")

    df.to_excel(final_name, index=False)
    return final_name

# --- GUI ---
def select_input_file():
    file_path = filedialog.askopenfilename(title="Selecciona l'arxiu de logs", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        input_file_var.set(file_path)

def select_output_folder():
    folder_path = filedialog.askdirectory(title="Selecciona la carpeta de sortida")
    if folder_path:
        output_folder_var.set(folder_path)

def generate_excel():
    input_file = input_file_var.get()
    output_folder = output_folder_var.get()

    if not input_file or not os.path.exists(input_file):
        messagebox.showerror("Error", "Selecciona un arxiu de logs vàlid.")
        return
    if not output_folder or not os.path.exists(output_folder):
        messagebox.showerror("Error", "Selecciona una carpeta de sortida vàlida.")
        return

    try:
        output_file = parse_logs(input_file, output_folder)
        messagebox.showinfo("Èxit", f"Excel generat correctament:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al generar l'Excel:\n{e}")

# --- Inicialización de GUI ---
root = tk.Tk()
root.title("Steering of Roaming - Log Parser")

input_file_var = tk.StringVar()
output_folder_var = tk.StringVar()

# Layout
tk.Label(root, text="Arxiu de logs:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
tk.Entry(root, textvariable=input_file_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Seleccionar...", command=select_input_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Carpeta de sortida:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Seleccionar...", command=select_output_folder).grid(row=1, column=2, padx=5, pady=5)

tk.Button(root, text="Generar Excel", command=generate_excel, width=20, bg='green', fg='white').grid(row=2, column=1, pady=20)

root.mainloop()