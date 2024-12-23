import sys
import os 

sys.path.append(os.path.join(os.path.dirname(__file__), 'finvizfinance'))   # modify sys path to include finviz dir (temp)

# to stop truncated output
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.width', 150)