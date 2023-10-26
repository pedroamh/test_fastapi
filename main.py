from fastapi import FastAPI
from handlers.webhook_handler import webhook_router
from fastapi.middleware.cors import CORSMiddleware

import uvicorn






app = FastAPI(timeout=30)



# Configurar el middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://survey123.arcgis.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar el tiempo de espera en la aplicación
@app.on_event("startup")
async def startup_event():
    app.timeout_seconds = 60  # Ajusta el tiempo de espera según tus necesidades (en segundos)


app.include_router(webhook_router, prefix="/webhook")

@app.get('/')
def index():
    return {"mensaje": "Hola"}
#wsgi_app = ASGIMiddleware(app)




# if __name__ == "__main__":
#     uvicorn.run("main:app", host="localhost", port=8000, timeout_keep_alive=10)