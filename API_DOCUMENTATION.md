# NID Mapping Service - API Documentation

**Base URL:** `http://localhost` (via Nginx) or `http://localhost:8000` (direct Django, dev only)

**Authentication:** JWT Bearer Token (all endpoints except `/api/token/` and `/api/token/refresh/`)

**Interactive Docs:** Swagger UI available at `http://localhost/api/docs/`

---

## Table of Contents

1. [Authentication](#1-authentication)
   - [Login (Obtain Token)](#11-login---obtain-jwt-token)
   - [Refresh Token](#12-refresh-token)
2. [NID Mapping](#2-nid-mapping)
   - [Map NID (POST)](#21-map-nid---post)
   - [Fetch NID (GET)](#22-fetch-nid---get)
3. [Response Fields Reference](#3-response-fields-reference)
4. [Error Responses](#4-error-responses)
5. [Test Data](#5-test-data)

---

## 1. Authentication

All protected endpoints require a JWT token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

Tokens expire after **1 day**. Use the refresh endpoint to get a new access token without re-logging in.

---

### 1.1 Login - Obtain JWT Token

Authenticate with username/password and receive access + refresh tokens.

**Endpoint:** `POST /api/token/`

**Auth Required:** No

**Request:**

| Field      | Type   | Required | Description       |
|:-----------|:-------|:---------|:------------------|
| `username` | string | Yes      | Django username    |
| `password` | string | Yes      | Django password    |

```bash
curl -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin-password"
  }'
```

**Response `200 OK`:**

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `401 Unauthorized`:**

```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 1.2 Refresh Token

Get a new access token using a valid refresh token.

**Endpoint:** `POST /api/token/refresh/`

**Auth Required:** No

**Request:**

| Field     | Type   | Required | Description                    |
|:----------|:-------|:---------|:-------------------------------|
| `refresh` | string | Yes      | Refresh token from login response |

```bash
curl -X POST http://localhost/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response `200 OK`:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `401 Unauthorized`:**

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

---

## 2. NID Mapping

### 2.1 Map NID - POST

Look up a citizen's NID record by their National Identification Number (`nin_loc`). The NIN is sent inside a wrapped `nid` object in the request body.

**Endpoint:** `POST /api/mapping/map/`

**Auth Required:** Yes (Bearer Token)

**Request Body:**

| Field         | Type   | Required | Description                              |
|:--------------|:-------|:---------|:-----------------------------------------|
| `nid`         | object | Yes      | Wrapper object containing NID fields      |
| `nid.nin_loc` | string | Yes      | National Identification Number (Devanagari format, e.g. `८९८-४१४-३७५-३`) |

> **Note:** The `nid` object can also include optional fields like `first_name`, `last_name`, `dob`, `gender`, etc. Currently, only `nin_loc` is used for the lookup. All other fields are validated but ignored.

**Minimal Request:**

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

**Full Request (all optional fields):**

```bash
curl -X POST http://localhost/api/mapping/map/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "nid": {
      "nin_loc": "८९८-४१४-३७५-३",
      "first_name": "SUNITA",
      "last_name": "SINTAN LAMA",
      "first_name_loc": "सुनिता",
      "last_name_loc": "सिन्तान लामा",
      "dob": "1990-06-15",
      "gender": "F"
    }
  }'
```

**Response `200 OK`:**

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
  "perm_state_loc": "3",
  "perm_district_loc": "32",
  "perm_rur_mun_loc": "362",
  "perm_ward_loc": "९",
  "perm_village_tol_loc": "मदनपथ",
  "cc_number_loc": "३११०२२/६५८४३",
  "cc_issuing_district_loc": "32",
  "cc_issuing_date_loc": "२०६६-०८-०४",
  "f_first_name_loc": "जित",
  "f_last_name_loc": "सिन्तान लामा",
  "m_first_name_loc": "शर्मिला",
  "m_last_name_loc": "सीन्तान लामा",
  "gf_first_name_loc": "कालु",
  "gf_last_name_loc": "सिन्तान लामा",
  "portrait_image": "AAAADGpQICANCocKAAAAFGZ0eXBqcDIg"
}
```

---

### 2.2 Fetch NID - GET

Fetch a citizen's NID record by passing the NIN as a query parameter.

**Endpoint:** `GET /api/mapping/fetch/`

**Auth Required:** Yes (Bearer Token)

**Query Parameters:**

| Parameter | Type   | Required | Description                              |
|:----------|:-------|:---------|:-----------------------------------------|
| `nin`     | string | Yes      | National Identification Number (Devanagari format) |

```bash
curl -X GET "http://localhost/api/mapping/fetch/?nin=८९८-४१४-३७५-३" \
  -H "Authorization: Bearer <access_token>"
```

**Response `200 OK`:**

Same response format as [Map NID (POST)](#21-map-nid---post) above.

---

## 3. Response Fields Reference

### Personal Information

| Field             | Type   | Description                                    | Example                |
|:------------------|:-------|:-----------------------------------------------|:-----------------------|
| `nin_loc`         | string | National ID Number (Devanagari)                | `८९८-४१४-३७५-३`       |
| `first_name`      | string | First name (English)                           | `SUNITA`               |
| `last_name`       | string | Last name (English)                            | `SINTAN LAMA`          |
| `first_name_loc`  | string | First name (Nepali/Devanagari)                 | `सुनिता`               |
| `last_name_loc`   | string | Last name (Nepali/Devanagari)                  | `सिन्तान लामा`         |
| `dob`             | string | Date of birth (AD, `YYYY-MM-DD`)               | `1990-06-15`           |
| `dob_loc`         | string | Date of birth (BS, Devanagari)                 | `२०४७-०३-०१`          |
| `gender`          | string | Gender (`M` = Male, `F` = Female)              | `F`                    |
| `portrait_image`  | string | Base64-encoded portrait image (JPEG 2000)      | `AAAADGpQICANCo...`   |

### Permanent Address

| Field                   | Type   | Description                           | Example      |
|:------------------------|:-------|:--------------------------------------|:-------------|
| `perm_state`            | string | State/Province code                   | `3`          |
| `perm_district`         | string | District code                         | `32`         |
| `perm_rur_mun`          | string | Rural municipality/Municipality code  | `362`        |
| `perm_ward`             | string | Ward number                           | `9`          |
| `perm_village_tol`      | string | Village/Tole name (English)           | `Madanpath`  |
| `perm_state_loc`        | string | State code (local)                    | `3`          |
| `perm_district_loc`     | string | District code (local)                 | `32`         |
| `perm_rur_mun_loc`      | string | Municipality code (local)             | `362`        |
| `perm_ward_loc`         | string | Ward number (Devanagari)              | `९`          |
| `perm_village_tol_loc`  | string | Village/Tole name (Nepali)            | `मदनपथ`      |

### Citizenship Certificate

| Field                      | Type   | Description                             | Example                    |
|:---------------------------|:-------|:----------------------------------------|:---------------------------|
| `cc_issuing_district`      | string | Issuing district code                   | `32`                       |
| `cc_issuing_date`          | string | Issuing date (AD, with time)            | `2009-11-19 00:00:00.0`    |
| `cc_number_loc`            | string | CC number (Devanagari)                  | `३११०२२/६५८४३`             |
| `cc_issuing_district_loc`  | string | Issuing district code (local)           | `32`                       |
| `cc_issuing_date_loc`      | string | Issuing date (BS, Devanagari)           | `२०६६-०८-०४`              |

### Family Information

| Field                | Type   | Description                          | Example          |
|:---------------------|:-------|:-------------------------------------|:-----------------|
| `f_first_name`       | string | Father's first name (English)        | `JIT`            |
| `f_last_name`        | string | Father's last name (English)         | `SINTAN LAMA`    |
| `f_first_name_loc`   | string | Father's first name (Nepali)         | `जित`            |
| `f_last_name_loc`    | string | Father's last name (Nepali)          | `सिन्तान लामा`   |
| `m_first_name`       | string | Mother's first name (English)        | `SHARMILA`       |
| `m_last_name`        | string | Mother's last name (English)         | `SINTAN LAMA`    |
| `m_first_name_loc`   | string | Mother's first name (Nepali)         | `शर्मिला`        |
| `m_last_name_loc`    | string | Mother's last name (Nepali)          | `सीन्तान लामा`   |
| `gf_first_name`      | string | Grandfather's first name (English)   | `KALU`           |
| `gf_last_name`       | string | Grandfather's last name (English)    | `SINTAN LAMA`    |
| `gf_first_name_loc`  | string | Grandfather's first name (Nepali)    | `कालु`           |
| `gf_last_name_loc`   | string | Grandfather's last name (Nepali)     | `सिन्तान लामा`   |

---

## 4. Error Responses

### 400 Bad Request — Validation Error

Returned when required fields are missing or the request body is malformed.

```json
{
  "nid": {
    "nin_loc": ["This field is required."]
  }
}
```

### 401 Unauthorized — Missing or Invalid Token

Returned when the `Authorization` header is missing, malformed, or the token has expired.

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

**Fix:** Call `POST /api/token/refresh/` with your refresh token, or re-login via `POST /api/token/`.

### 404 Not Found — NIN Not Found

Returned when the given NIN does not match any record.

```json
{
  "error": "No NID data found for NIN: ९९९-९९९-९९९-९"
}
```

### 500 Internal Server Error

Returned on unexpected server errors.

```json
{
  "error": "Internal Error: <error details>"
}
```

---

## 5. Test Data

Mock mode is enabled by default (`NID_MOCK_ENABLED=True`). Use these NINs for testing:

| NIN (nin_loc)           | Name                 | Gender | DOB (AD)     | Location     |
|:------------------------|:---------------------|:-------|:-------------|:-------------|
| `८९८-४१४-३७५-३`        | SUNITA SINTAN LAMA   | F      | 1990-06-15   | Madanpath    |
| `१२३-४५६-७८९-०`        | RAM BAHADUR THAPA    | M      | 1985-03-22   | Baluwatar    |
| `५५५-१२३-९८७-६`        | GITA SHARMA          | F      | 1992-11-05   | Dharan       |
| `७७७-८८८-९९९-१`        | BIKASH GURUNG        | M      | 1988-01-10   | Pokhara      |
| `३३३-२२२-१११-४`        | ANITA ADHIKARI       | F      | 1995-08-30   | Butwal       |
| `६६६-५५५-४४४-२`        | SANJAY MAHARJAN      | M      | 1982-12-25   | Lalitpur     |
| `१११-२२२-३३३-५`        | PRAMILA TAMANG       | F      | 1998-04-18   | Bhaktapur    |
| `४४४-३३३-२२२-७`        | DEEPAK KC            | M      | 1975-07-07   | Nepalgunj    |
| `९९९-८८८-७७७-८`        | SABINA RAI           | F      | 2000-02-14   | Biratnagar   |
| `२२२-१११-०००-९`        | RAJESH SHRESTHA      | M      | 1979-09-20   | Kathmandu    |

---

## Quick Start — Full Flow Example

```bash
# Step 1: Login
TOKEN=$(curl -s -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin-password"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

echo "Token: $TOKEN"

# Step 2: Fetch NID via GET
curl -s -X GET "http://localhost/api/mapping/fetch/?nin=८९८-४१४-३७५-३" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Step 3: Map NID via POST
curl -s -X POST http://localhost/api/mapping/map/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nid": {
      "nin_loc": "१२३-४५६-७८९-०"
    }
  }' | python3 -m json.tool

# Step 4: Refresh token when it expires
REFRESH=$(curl -s -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin-password"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['refresh'])")

curl -s -X POST http://localhost/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH\"}" | python3 -m json.tool
```

---

## Integration Notes

- **All traffic** goes through Nginx (port 80) → OpenHIM (port 5001) → Django (port 8000)
- OpenHIM channel is **public** — no auth at the OpenHIM layer; Django handles JWT auth
- `_loc` suffix fields contain **Nepali/Devanagari** script values
- Fields without `_loc` suffix are in **English**
- `portrait_image` contains a **base64-encoded JPEG 2000** image (truncated in test data)
- `dob` is in **AD (Gregorian)** format; `dob_loc` is in **BS (Bikram Sambat)** format
- `cc_issuing_date` includes time component (`00:00:00.0`); `cc_issuing_date_loc` is date-only in BS
- Token lifetime: **Access = 1 day**, **Refresh = 1 day** (configurable in Django settings)
