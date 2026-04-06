def get_mediator_metadata():
    """
    Returns the OpenHIM mediator registration metadata.
    """
    return {
        "urn": "urn:mediator:nid-mapping-service",
        "name": "NID Mapping Mediator",
        "version": "1.0.0",
        "description": "Mediator to map National ID data to standardized SPDCI/Group structures.",
        "endpoints": [
            {
                "name": "NID Mapping Endpoint",
                "host": "nid-map-service", # Container name in docker
                "path": "/api/mapping/map/",
                "port": "8000",
                "primary": True,
                "type": "http"
            },
            {
                "name": "NID Fetch and Map Endpoint",
                "host": "nid-map-service",
                "path": "/api/mapping/fetch/",
                "port": "8000",
                "primary": False,
                "type": "http"
            }
        ],
        "defaultChannelConfig": [
            {
                "name": "NID Mapping Channel",
                "urlPattern": "^/api/.*",
                "alerts": {
                    "fail": False,
                    "success": False
                },
                "allow": [],
                "authType": "public",
                "methods": ["GET", "POST", "PUT", "DELETE"],
                "type": "http",
                "routes": [
                    {
                        "name": "NID Service Route",
                        "host": "nid-map-service",
                        "pathTransform": "",
                        "port": "8000",
                        "primary": True,
                        "type": "http",
                        "forwardAuthHeader": True
                    }
                ]
            }
        ]
    }

def get_client_metadata():
    """
    Returns the OpenHIM client metadata.
    """
    return {
        "name": "NID Mapping Client",
        "urn": "urn:client:nid-mapping-client",
        "clientID": "nid-mapping-client",
        "password": "client-password",
        "roles": ["read-only"]
    }
