# NID Mapping Service - OpenHIM Integration Guide

This guide documents the final working configuration and testing parameters for the NID Mapping Service integrated with OpenHIM.

## 🚀 Final Verified Testing Command

Use the following command to test the end-to-end flow through the OpenHIM Channel (Port 5001). This command is verified to pass authentication and reach the Django backend correctly.

```bash
curl -v -u "test:test" -X POST http://localhost:5001/api/mapping/map/ \
  -H "Content-Type: application/json" \
  -d '{
    "nid": {
      "nin_loc": "2026-Verification",
      "first_name": "Final",
      "last_name": "Test"
    }
  }'
```

---

## 🔐 Credentials & Ports

| Component | Port | User / ID | Password |
| :--- | :--- | :--- | :--- |
| **OpenHIM Channel** | `5001` | `test` | `test` |
| **OpenHIM Console** | `8080` (API) | `root@openhim.org` | `password` |
| **Django Service** | `8000` | N/A | N/A |

---

## 📁 System Persistence
*   **Database Data**: MongoDB and Postgres data are stored in named volumes (`mongodb_data`, `postgres_data`) and will persist across container restarts.
*   **Configuration**: All environment variables are centralized in the `.env` file.

## 🛠 Troubleshooting
If you receive a `401 Unauthorized` through Port 5001, ensure the `test` client is active and has the correct password set in the OpenHIM Console at `http://localhost:9000`.
