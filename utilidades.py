import pandas as pd
import json

def get_json(_json:dict):
    json_ = json.loads(json.dumps(_json))
    return json_

def get_attachments(df:pd.DataFrame):
    cols = ['globalId','parentGlobalId','name','contentType','keywords','size','id','url']

    df2 = pd.DataFrame(columns = cols)
    for i in df['feature']['repeats']['integrantes']:
        l = get_json(i['attachments'])
        for foto in l['foto']:
            df2.loc[len(df2.index)] = foto
    return df2

def get_repeats(df:pd.DataFrame):
    cols_int = ['integrante','parentglobalid','globalid']
    df1 = pd.DataFrame(columns = cols_int)
    for item in df['feature']['repeats']['integrantes']:
        reg = get_json(item['attributes'])   
        df1.loc[len(df1.index)] = reg
        
    return df1 