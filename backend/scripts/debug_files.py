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

def debug_files(orulo_id):
    print(f"--- Debugging Files for Imovel {orulo_id} ---")
    
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
    
    # 1. Main Endpoint to see if files are listed there
    print("\n1. endpoint /buildings/{id}")
    r = requests.get(f"{base_url}/buildings/{orulo_id}", headers=headers)
    if r.status_code == 200:
        data = r.json()
        files = data.get('files', [])
        print(f"  - 'files' count: {len(files)}")
        print(f"  - 'files' data: {files}")
        
        # Check if keys exist
        if files:
            print(f"  - First file keys: {files[0].keys()}")

    # 2. Endpoint /files
    print("\n2. endpoint /buildings/{id}/files")
    r2 = requests.get(f"{base_url}/buildings/{orulo_id}/files", headers=headers)
    print(f"  Status: {r2.status_code}")
    if r2.status_code == 200:
        print(f"  Data: {r2.text}")
    
    # 3. Endpoint /images to see if maybe files are mixed in?
    # Unlikely based on docs.

# Get first Orulo imovel
imovel = Imovel.objects.filter(is_orulo=True).first()
if imovel:
    debug_files(imovel.orulo_id)
else:
    print("Nenhum imovel Orulo encontrado no banco.")
