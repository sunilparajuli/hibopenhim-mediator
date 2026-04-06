import requests
from django.conf import settings
from .dummy_data import DUMMY_NID_DATA


class NIDClient:
    """
    Client for fetching data from the external NID API.
    """
    def __init__(self, use_mock=False):
        self.api_url = getattr(settings, 'NID_API_URL', 'https://api.nidmc.gov.np/v1/person/')
        self.api_key = getattr(settings, 'NID_API_KEY', 'default-key')
        self.timeout = getattr(settings, 'NID_API_TIMEOUT', 10)
        self.verify_ssl = getattr(settings, 'VERIFY_SSL', True)
        self.use_mock = use_mock

    def fetch_by_nin(self, nin):
        """
        Fetches NID data by National Identifier (NIN).
        """
        if self.use_mock:
            return self._get_mock_response(nin)

        endpoint = f"{self.api_url}{nin}/"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        try:
            response = requests.get(
                endpoint,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"NIN {nin} not found.") from e
            raise Exception(f"External API error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection to NID Service failed: {e}") from e

    def _get_mock_response(self, nin):
        """
        Returns dummy data looked up by NIN key.
        """
        if nin in DUMMY_NID_DATA:
            return DUMMY_NID_DATA[nin]
        raise ValueError(f"NIN {nin} not found in dummy data.")
