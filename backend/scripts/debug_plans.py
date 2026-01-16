import os
import django
import requests
import json
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from imoveis.models import Imovel

def debug_floor_plans(orulo_id):
    print(f"--- Debugging Floor Plans for Imovel {orulo_id} ---")
    
    # Auth
    url_auth = "https://www.orulo.com.br/oauth/token"
    payload = {
        "client_id": settings.ORULO_CLIENT_ID,
        "client_secret": settings.ORULO_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    resp_auth = requests.post(url_auth, data=payload)
    token = resp_auth.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    base_url = settings.ORULO_BASE_URL
    
    # 3. Floor Plans
    print("\n3. endpoint /buildings/{id}/floor_plans")
    url_plans = f"{base_url}/buildings/{orulo_id}/floor_plans"
    params = {'dimensions[]': '1024x1024'}
    r_plan = requests.get(url_plans, headers=headers, params=params)
    if r_plan.status_code == 200:
        d_plan = r_plan.json().get('floor_plans', [])
        print(f"  - Floor plans count: {len(d_plan)}")
        for plan in d_plan:
            print(f"    PLAN FULL: {plan}")
    else:
        print(f"  Error: {r_plan.status_code}")

    # 4. Typologies
    print("\n4. endpoint /buildings/{id}/typologies")
    r_typ = requests.get(f"{base_url}/buildings/{orulo_id}/typologies", headers=headers, params={'include[]': 'not_available'})
    if r_typ.status_code == 200:
        d_typ = r_typ.json().get('typologies', [])
        print(f"  - Typologies count: {len(d_typ)}")
        for typ in d_typ:
            print(f"    TYPOLOGY: id={typ.get('id')}, type={typ.get('type')}")
            print(f"              keys={list(typ.keys())}")
    else:
        print(f"  Error: {r_typ.status_code}")

# Get first Orulo imovel
imovel = Imovel.objects.filter(is_orulo=True).first()
if imovel:
    debug_floor_plans(imovel.orulo_id)
else:
    print("Nenhum imovel Orulo encontrado no banco.")
