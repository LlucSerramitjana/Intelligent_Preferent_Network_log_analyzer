import pandas as pd
import re

LOG_FILE = 'logs.txt'
OUTPUT_EXCEL = 'steering_events.xlsx'

VALID_ACTIONS = ['UNEXPECTED_DATA_VALUE', 'DIAMETER_UNABLE_TO_COMPLY', 'RELAY']

rows = []

with open(LOG_FILE, 'r', encoding='utf-8') as f:
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

        # Extraer IPNLogic y PNLogic con regex
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

# Crear DataFrame y guardar Excel
FIELDS = ['IMSI', 'Timestamp', 'Operator', 'Country', 'Action', 'Description', 'IPNLogic']
df = pd.DataFrame(rows, columns=FIELDS)
df.to_excel(OUTPUT_EXCEL, index=False)

print(f'Excel generado correctamente: {OUTPUT_EXCEL}')