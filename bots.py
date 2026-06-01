import os
import django
import requests
import time
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TicketAPI_Poncho.settings') 
django.setup()

from apps.usuario.models import Usuario 

URL_TOKEN = "http://127.0.0.1:8000/api/token/"
URL_COMPRA = "http://127.0.0.1:8000/index/ticket/"

SECTORES = [    #la uuid de los cosos
# no me da la cabeza para hacer esto de una forma mas bonita 
    "fa6f6879-afa2-4017-af4b-b4e97f25f1a2",
    "53a31445-aa58-45b0-92dd-234d6071afc0",
    "8e8a00cb-19bd-4d93-a0ff-ec63d460d7c3"
]

def ataque_ddods(cantidad_bots=300):
    
    coso = 'coso'
    for i in range(cantidad_bots):
        username_bot = f"bot_{coso}{i}"
        password_bot = "1111"

        Usuario.objects.create_user(
            username=username_bot, 
            password=password_bot, 
            rol='comprador'
        )
        
        res_token = requests.post(URL_TOKEN, json={"username": username_bot, "password": password_bot})
        
        if res_token.status_code != 200:
            print(f"[{i}/{cantidad_bots}] Es tonto, {username_bot}: {res_token.text}")
            continue
            
        token = res_token.json().get('access')
        headers = {"Authorization": f"Bearer {token}"} # El token va en la cabeza de las peticiones asi (segun chatgpt)

        sector = random.choice(SECTORES)
        payload = {
            "sector_entrada": sector, 
            "cantidad": random.randint(1, 4)
        }
        
        requests.post(URL_COMPRA, json=payload, headers=headers)
        time.sleep(random.uniform(1.0, 4.0))

if __name__ == "__main__":
    ataque_ddods()