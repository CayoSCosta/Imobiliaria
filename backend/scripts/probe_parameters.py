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

def probe():
    print(f"--- Probing Parameters ---")
    
    url_auth = "https://www.orulo.com.br/oauth/token"
    payload = {
        "client_id": settings.ORULO_CLIENT_ID,
        "client_secret": settings.ORULO_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    try:
        resp_auth = requests.post(url_auth, data=payload)
        resp_auth.raise_for_status()
        token = resp_auth.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        base_url = settings.ORULO_BASE_URL
    except Exception as e:
        print(f"Auth failed: {e}")
        return

    # Check one imovel
    imovel = Imovel.objects.filter(is_orulo=True).first()
    if not imovel:
        print("No orulo imovel found")
        return

    url = f"{base_url}/buildings/{imovel.orulo_id}"
    print(f"Testing {imovel.orulo_id}")

    # Test Global Endpoints
    print("Testing Global Endpoints:")
    global_resources = ['files', 'documents', 'attachments', 'marketing']
    
    for res in global_resources:
        g_url = f"{base_url}/{res}"
        try:
            r_glob = requests.get(g_url, headers=headers, params={'building_id': imovel.orulo_id})
            print(f"GET /{res}?building_id={imovel.orulo_id} -> {r_glob.status_code}")
        except:
            pass



if __name__ == "__main__":
    probe()
