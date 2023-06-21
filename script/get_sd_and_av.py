import os
from typing import Dict
from natsort import natsorted
import pandas as pd
import re
from statistics import stdev, mean

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FOLDER = os.path.join(THIS_FOLDER, "summary_sdav")
RESULT_FOLDER = os.path.join(THIS_FOLDER, "result_sdav")

def get_res(path):
    file = open(path, 'r')
    nama = path
    content = file.readlines()
    res = dict()
    fail = dict()

    for data in content:
        data = data.strip()
        if data.startswith("[") and data.endswith("]"):
            information_inside_bracket = re.findall(r"\[.*?\]", data)
            temp = information_inside_bracket[0].strip("[]").strip().split(" ")
            method = temp[0]
            path = temp[1]
            concurrency = temp[2]
            key = f'{method} {path}'
        if 'transaction_rate' in data:
            data = data.replace('\t', '').replace(' ','')
            value = data.split(':')[1].strip(',')
            try:
                res[key].append(float(value))
            except:
                res[key] = [float(_) for _ in value.split()]
        if 'availability' in data:
            data = data.replace('\t', '').replace(' ','')
            value = float(data.split(':')[1].strip(','))
            if value < 100:
                try:
                    fail[key] = 1
                except:
                    fail[key] += 1

    file = nama.split('/')[-1].split('.')[0]
    rata = 0
    fail_list = []
    if len(res.items()) > 3:
        value_std = []
        value_rat = []
    else:
        value_std = [0,0]
        value_rat = [0,0]

    for key, val in res.items():
        rata += mean(val)
        print(key,':','\n\tstandar deviasi :',stdev(val),'\n\trataan \t\t:',mean(val))
        value_std.append(stdev(val))
        value_rat.append(mean(val))
    # value_rat.append(rata/len(res.items()))
    # df[file] = value_rat

    for x in df['endpoint']:
        try:
            fail_list.append(fail[x])
        except:
            fail_list.append(0)
    df[file] = fail_list
    print(df)
    print('rataan total :',rata/len(res.items()))
    print('ketika memory 100% :',fail)

df : Dict[str, list] = {}
df["endpoint"] = ['GET /node/', 'GET /node/1', 'PUT /node/1', 'POST /channel/']
for file in natsorted(os.listdir(RESULT_FOLDER)):
    print('-----------------------------')
    print('Konfigurasi :',file.split('.')[0])
    full_path = os.path.join(RESULT_FOLDER, file)
    get_res(full_path)

print(df)
excel = pd.DataFrame(df)
excel.to_excel('memori_100%.xlsx')