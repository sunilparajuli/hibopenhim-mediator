import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nid_map_service_project.settings')
django.setup()

from django.conf import settings
from rest_framework.test import APIClient

def verify_dev_mode():
    client = APIClient()
    nin = "८९८-४१४-३७५-३"
    
    print(f"Verifying with DEV_MODE = {settings.DEV_MODE}")
    
    # 1. Test fetch endpoint without authentication
    response = client.get(f'/api/mapping/fetch/?nin={nin}')
    print(f"Fetch (Unauthenticated) Status: {response.status_code}")
    
    if settings.DEV_MODE:
        assert response.status_code == 200
        print("PASS: Accessible without token in DEV_MODE")
    else:
        assert response.status_code == 401
        print("PASS: Authentication enforced when DEV_MODE is False")

if __name__ == "__main__":
    verify_dev_mode()
