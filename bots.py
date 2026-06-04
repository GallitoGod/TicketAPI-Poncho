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
    "efd5e471-ec9a-40e8-bd88-1f9166c1be47",
    "8fd5e5ec-4323-4e3c-adb9-1a89abb6020a",
    "3e1a1873-f47d-4bb3-a600-d05d9f200406",
    "f499c724-2671-424d-be1f-759da55bea4a",
    "3739ab72-e8b4-49c1-b9b3-c5a31bc58bf5",
    "afe9c7da-0b77-43e0-822a-768c59855a46"
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
            print(f"{username_bot} es tonto: {res_token.text}")
            continue
            
        token = res_token.json().get('access')
        headers = {"Authorization": f"Bearer {token}"} # El token va en la cabeza de las peticiones

        sector = random.choice(SECTORES)
        payload = {
            "sector_entrada": sector, 
            "cantidad": random.randint(1, 4)
        }
        
        requests.post(URL_COMPRA, json=payload, headers=headers)
        time.sleep(random.uniform(0.3,1.0))

if __name__ == "__main__":
    ataque_ddods()