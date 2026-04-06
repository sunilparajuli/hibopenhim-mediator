# NID Mapping Mediator Service

A Django-based mediator service integrated with OpenHIM that maps Nepal National ID (NID) data. Nginx sits in front as a reverse proxy on port 80, routing API traffic through OpenHIM to Django.

## Architecture

```
                         +--> OpenHIM Console (UI)
                         |
Client --> Nginx (80) ---+--> OpenHIM (5001) --> Django (8000)
                         |      public             JWT auth
Browser --> Nginx (8080) +--> OpenHIM Core API (8080/HTTPS)
```

- **Nginx** is the single entry point — proxies port 80 for API + Console, port 8080 for OpenHIM Core API
- **OpenHIM** acts as a transparent proxy (public channel, no auth at this layer)
- **Django** protects its own routes using JWT (`IsAuthenticated`)
- On startup, Django auto-registers the mediator and channel config with OpenHIM

## Exposed Ports

| Port   | Service via Nginx            | Description                              |
|:-------|:-----------------------------|:-----------------------------------------|
| `80`   | `/api/*` -> OpenHIM -> Django | Main API (login, mapping, swagger)       |
| `80`   | `/*` -> OpenHIM Console       | OpenHIM management UI                   |
| `8080` | OpenHIM Core API (HTTPS)     | Needed for console login (SSL proxied)   |
| `8000` | Django direct (dev only)     | Bypass OpenHIM — remove in production    |

Internal services (not exposed to host):
- OpenHIM Core: `5000`, `5001`, `8080`
- PostgreSQL: `5432`
- MongoDB: `27017`

## Quick Start

```bash
# Clone and start all services
git clone https://github.com/sunilparajuli/hibopenhim-mediator.git
cd hibopenhim-mediator
docker compose up --build -d

# Wait ~15 seconds for OpenHIM registration to complete
docker logs nid-map-service --tail 10
```

You should see:
```
Successfully registered mediator with OpenHIM.
Successfully updated channel: NID Mapping Channel
```

## Credentials

| Component          | Username            | Password           |
|:-------------------|:--------------------|:-------------------|
| Django Admin/API   | `admin`             | `admin-password`   |
| OpenHIM Console    | `root@openhim.org`  | `password`         |

## First-Time OpenHIM Console Setup

The OpenHIM Core API uses a self-signed SSL certificate. On first use:

1. Open **`https://localhost:8080`** in your browser
2. You will see a security warning — click **Advanced** > **Proceed / Accept Risk**
3. You should see a JSON response or blank page — that's fine, the cert is now trusted by your browser
4. Now open **`http://localhost`** (the console via Nginx)
5. Login with `root@openhim.org` / `password`
6. The channel **NID Mapping Channel** should already be auto-created with:
   - URL Pattern: `^/api/.*`
   - Auth Type: `public`
   - Routes all `/api/` traffic to Django container on port 8000

> **Note:** Step 1-3 is a one-time browser action. Once accepted, the console works normally.

## API Endpoints

All requests go through **`http://localhost`** (port 80, via Nginx).

### 1. Login (Get JWT Token)

```bash
curl -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin-password"}'
```

Response:
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### 2. Refresh Token

```bash
curl -X POST http://localhost/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

### 3. Map NID (POST)

Looks up NID data by `nin_loc` from the request body.

```bash
curl -X POST http://localhost/api/mapping/map/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "nid": {
      "nin_loc": "८९८-४१४-३७५-३"
    }
  }'
```

### 4. Fetch NID (GET)

Fetches NID data by `nin` query parameter.

```bash
curl -X GET "http://localhost/api/mapping/fetch/?nin=८९८-४१४-३७५-३" \
  -H "Authorization: Bearer <access_token>"
```

### 5. Swagger Docs

- Swagger UI: `http://localhost/api/docs/`
- ReDoc: `http://localhost/api/redoc/`
- OpenAPI Schema: `http://localhost/api/schema/`

### 6. Django Admin (direct, dev only)

`http://localhost:8000/admin/`

## Available Test NINs (Dummy Data)

Mock mode is enabled by default (`NID_MOCK_ENABLED=True`). The following NINs return dummy data:

| NIN                 | Name               | Gender | Location     |
|:--------------------|:-------------------|:-------|:-------------|
| `८९८-४१४-३७५-३`    | SUNITA SINTAN LAMA | F      | Madanpath    |
| `१२३-४५६-७८९-०`    | RAM BAHADUR THAPA  | M      | Baluwatar    |
| `५५५-१२३-९८७-६`    | GITA SHARMA        | F      | Dharan       |
| `७७७-८८८-९९९-१`    | BIKASH GURUNG      | M      | Pokhara      |
| `३३३-२२२-१११-४`    | ANITA ADHIKARI     | F      | Butwal       |
| `६६६-५५५-४४४-२`    | SANJAY MAHARJAN    | M      | Lalitpur     |
| `१११-२२२-३३३-५`    | PRAMILA TAMANG     | F      | Bhaktapur    |
| `४४४-३३३-२२२-७`    | DEEPAK KC          | M      | Nepalgunj    |
| `९९९-८८८-७७७-८`    | SABINA RAI         | F      | Biratnagar   |
| `२२२-१११-०००-९`    | RAJESH SHRESTHA    | M      | Kathmandu    |

Any NIN not in this list returns a `404` error.

## Sample Response

```json
{
  "nin_loc": "८९८-४१४-३७५-३",
  "first_name": "SUNITA",
  "last_name": "SINTAN LAMA",
  "first_name_loc": "सुनिता",
  "last_name_loc": "सिन्तान लामा",
  "dob": "1990-06-15",
  "dob_loc": "२०४७-०३-०१",
  "gender": "F",
  "perm_state": "3",
  "perm_district": "32",
  "perm_rur_mun": "362",
  "perm_ward": "9",
  "perm_village_tol": "Madanpath",
  "cc_issuing_district": "32",
  "cc_issuing_date": "2009-11-19 00:00:00.0",
  "f_first_name": "JIT",
  "f_last_name": "SINTAN LAMA",
  "m_first_name": "SHARMILA",
  "m_last_name": "SINTAN LAMA",
  "gf_first_name": "KALU",
  "gf_last_name": "SINTAN LAMA",
  "perm_ward_loc": "९",
  "perm_village_tol_loc": "मदनपथ",
  "cc_number_loc": "३११०२२/६५८४३",
  "cc_issuing_date_loc": "२०६६-०८-०४",
  "portrait_image": "AAAADGpQICANCocKAAAAFGZ0eXBqcDIg"
}
```

## Project Structure

```
.
├── docker-compose.yml              # All services (Nginx, Django, OpenHIM, Postgres, MongoDB)
├── Dockerfile                      # Django app image
├── entrypoint.sh                   # Runs migrations + runserver
├── requirements.txt                # Python dependencies
├── manage.py
├── docker-compose.prod.yml         # Production overrides (SSL, certbot, no debug)
├── nginx/
│   ├── Dockerfile                  # Custom nginx image with openssl
│   ├── default.conf                # Dev nginx config (localhost)
│   ├── production.conf             # Production nginx config (domain + Let's Encrypt)
│   ├── console.production.json     # Console config for production (uses /openhim-api/ path)
│   ├── console.config.js           # Console config for dev
│   └── generate-certs.sh           # Auto-generates self-signed SSL certs (dev only)
├── nid_map_service_project/
│   ├── settings.py                 # Django settings (JWT, DB, OpenHIM config)
│   ├── urls.py                     # Root URLs (token, mapping, swagger)
│   └── wsgi.py
└── mapping/
    ├── views.py                    # API views (NIDMappingView, NIDMediatorView)
    ├── urls.py                     # /map/ and /fetch/ routes
    ├── serializers.py              # DRF serializers
    ├── models.py                   # APILog model
    ├── middleware.py               # Request logging middleware
    ├── apps.py                     # Auto-registers mediator on startup
    ├── openhim/
    │   ├── config.py               # OpenHIM channel/mediator config
    │   └── register.py             # Registration logic with retries
    └── services/
        ├── client.py               # NIDClient (mock + real API)
        ├── dummy_data.py           # 10 dummy NID records keyed by NIN
        └── mapper.py               # SPDCI mapper (commented out for now)
```

## Environment Variables

Set in `docker-compose.yml` under the `web` service:

| Variable               | Default                     | Description                      |
|:-----------------------|:----------------------------|:---------------------------------|
| `DATABASE_URL`         | postgres://...@db:5432/...  | PostgreSQL connection string     |
| `SECRET_KEY`           | (insecure default)          | Django secret key                |
| `DEBUG`                | `True`                      | Django debug mode                |
| `NID_MOCK_ENABLED`     | `True`                      | Use dummy data instead of real API |
| `OPENHIM_URL`          | `https://openhim-core:8080` | OpenHIM Management API URL       |
| `OPENHIM_API_USERNAME` | `root@openhim.org`          | OpenHIM admin username           |
| `OPENHIM_API_PASSWORD` | `password`                  | OpenHIM admin password           |
| `VERIFY_SSL`           | `False`                     | SSL verification for OpenHIM     |

## Development Notes

- Code is volume-mounted (`.:/app`), so edits are picked up automatically by `runserver`
- No need to rebuild or restart for code changes during development
- SPDCI mapping (`services/mapper.py`) is commented out — endpoints return raw NID key-value data for now
- JWT access tokens expire in 1 day (configurable in `settings.py` under `SIMPLE_JWT`)
- To create additional Django users: `docker exec -it nid-map-service python manage.py createsuperuser`

## Production Deployment (with domain)

When deploying with a real domain, Nginx handles SSL via Let's Encrypt and proxies the OpenHIM Core API through a path — so no more self-signed cert issues.

**Architecture with domain:**
```
https://your-domain.com/api/*          → OpenHIM (5001) → Django
https://your-domain.com/openhim-api/*  → OpenHIM Core API (8080)
https://your-domain.com/*              → OpenHIM Console UI
```

**Setup steps:**

```bash
# 1. Replace YOUR_DOMAIN in these files with your actual domain:
sed -i 's/YOUR_DOMAIN/your-domain.com/g' nginx/production.conf
sed -i 's/YOUR_DOMAIN/your-domain.com/g' nginx/console.production.json
sed -i 's/your-email@example.com/you@example.com/g' docker-compose.prod.yml
sed -i 's/YOUR_DOMAIN/your-domain.com/g' docker-compose.prod.yml

# 2. First run — get SSL cert (nginx must be running on port 80 for the challenge):
#    Temporarily start with a basic HTTP config, then run certbot:
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot

# 3. Restart nginx to pick up the new cert:
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx
```

**Key files for production:**
- `nginx/production.conf` — SSL-terminated nginx config with Let's Encrypt
- `nginx/console.production.json` — tells OpenHIM Console to use `/openhim-api/` path instead of port 8080
- `docker-compose.prod.yml` — overrides: removes exposed ports, adds certbot, disables debug

**Auto-renew certs (add to crontab):**
```bash
0 3 * * * cd /path/to/project && docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx
```

## Data Persistence

- **PostgreSQL** data: `postgres_data` named volume
- **MongoDB** data: `mongodb_data` named volume
- Data persists across container restarts. To reset: `docker compose down -v`
