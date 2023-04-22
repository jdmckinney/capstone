import pandas as pd
import numpy as np

def gen_cols(len):
    test = [[x/len,y/len] for x in range(len) for y in range(len)]
    df = pd.DataFrame((test + (0.15 * np.random.rand(len*len, 2))) / [25,25] + [40.75480, -111.888138] - [0.02,0.025], columns=['lat','lon'])
    df['mean'] = np.random.randint(10, high=100, size = len * len)
    return df

df = gen_cols(10)

compression_opts = dict(method='zip', archive_name='stations.csv')
df.to_csv('stations.zip', index=False, compression=compression_opts)