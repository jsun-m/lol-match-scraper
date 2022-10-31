import json
import pandas as pd

f = open("scraped_data/data.json", "r")

data = json.loads(f.read())

print(pd.DataFrame.from_dict(data))