import sys
import pandas as pd

def get_param_value(csv_file, run_name, parameter):
    df = pd.read_csv(csv_file)
    row = df[df['name'] == run_name]
    if parameter not in df.columns:
        print(f"Parameter {parameter} not found.")
        return

    if not row.empty:
        print(row.iloc[0][parameter])
    else:
        print(f"Run name '{run_name}' not found.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <csv_file> <run_name> <parameter>")
    else:
        get_param_value(sys.argv[1], sys.argv[2], sys.argv[3])
