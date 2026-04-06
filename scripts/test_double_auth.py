import requests
import json
import base64

# Configuration
OPENHIM_URL = "http://localhost:5001/api/mapping/map/"
DJANGO_TOKEN_URL = "http://localhost:8000/api/token/"

# Credentials
OPENHIM_USER = "test"
OPENHIM_PASS = "test"
DJANGO_USER = "admin"
DJANGO_PASS = "admin-password"

def get_jwt_token():
    """Obtains a JWT Access Token from Django."""
    print(f"[*] Obtaining JWT token for user: {DJANGO_USER}...")
    response = requests.post(
        DJANGO_TOKEN_URL,
        json={"username": DJANGO_USER, "password": DJANGO_PASS}
    )
    if response.status_code == 200:
        token = response.json().get("access")
        print("[+] Token obtained successfully.")
        return token
    else:
        print(f"[-] Failed to obtain token: {response.text}")
        return None

def test_mapping_service(jwt_token):
    """Calls the NID Mapping service through OpenHIM with Double Auth."""
    print(f"[*] Sending request to OpenHIM at {OPENHIM_URL}...")
    
    # 1. OpenHIM Basic Auth
    # requests.auth.HTTPBasicAuth(OPENHIM_USER, OPENHIM_PASS)
    
    # 2. Django JWT Auth Header
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jwt_token}"
    }
    
    # Payload
    payload = {
        "nid": {
            "nin_loc": "PYTHON-DOUBLE-AUTH-TEST",
            "first_name": "Python",
            "last_name": "Mediator"
        }
    }
    
    # Execute (Passing Basic Auth and separate Bearer header)
    # Note: requests will merge Basic Auth into the 'Authorization' header.
    # To keep BOTH, we must use a custom header for one of them or rely on OpenHIM forwarding.
    # Since OpenHIM Core consumes 'Authorization' for its own auth, we send OpenHIM auth 
    # and put the JWT in X-Authorization (which we configured Django to accept).
    
    double_auth_headers = {
        "Content-Type": "application/json",
        "X-App-Authorization": f"Bearer {jwt_token}"
    }

    response = requests.post(
        OPENHIM_URL,
        auth=(OPENHIM_USER, OPENHIM_PASS),
        headers=double_auth_headers,
        json=payload
    )
    
    print(f"[*] Status Code: {response.status_code}")
    print(f"[*] Response Body: {response.text}")

if __name__ == "__main__":
    token = get_jwt_token()
    if token:
        test_mapping_service(token)
