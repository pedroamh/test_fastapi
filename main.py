from fastapi import HTTPException
from fastapi import Response, Request
from fastapi import FastAPI
from database import Foto, Integrante, Persona, database as connection
from database import User
from schemas import UserRequestModel, UserResponseModel
import json
import pandas as pd
import utilidades as ut
import urllib.request
import uvicorn

app = FastAPI(title='Test fast API',
              description='test',
              version='1.0')




@app.get('/')
def index():
    return 'Hola mundo'


@app.post('/users')
def create_user(user_request:UserRequestModel):
    user = User.create(
        username= user_request.username,
        email= user_request.email
    )
    return user_request

@app.get('/users/{user_id}')
def get_user(user_id):
    user = User.select().where(User.id == user_id).first()
    if user:
        return UserResponseModel(
            id=user.id,
            username=user.username,
            email=user.email
        )
    else:
        return HTTPException(404, 'User not found')

@app.post('/webhook')
async def webhook(request: Request):
    req = await request.json()
    
    
    df = pd.DataFrame.from_dict(req)
    
    print(req)
    token = df['portalInfo']['token']
    x = df['feature']['geometry']['x']
    y = df['feature']['geometry']['y']
    
    nombre = df['feature']['attributes']['nombre']
    globalid = df['feature']['attributes']['globalid']
    
    persona = Persona.create(
        nombre = nombre,
        globalId = globalid,
        x = x,
        y = y
    )
    
    integrantes_df = ut.get_repeats(df)
    
    for index, row1 in integrantes_df.iterrows():        
        int_nombre = row1['integrante']
        gid = row1['globalid']
    
        integrante = Integrante.create(
            integrante = int_nombre,
            persona = persona
        )
    
        attachs_df = ut.get_attachments(df)
        for index, row2 in attachs_df.iterrows():
            if row2['parentGlobalId'] == gid:
                url_d = row2['url']+'?token='+token
                urllib.request.urlretrieve(url_d, 'Fotos/'+row2['name'])
                foto = Foto.create(
                    url = 'Fotos/'+row2['name'],
                    integrante = integrante
                )

@app.post('/prueba')
async def webhook_test(request: Request):
    req = await request.json()
    print(req)



if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, timeout_keep_alive=10)
