from datetime import datetime

def format_date_to_iso(date_str):
    """
    Converts 2009-11-19 00:00:00.0 to 2009-11-19T00:00:00Z
    Also handles 1990-06-15 to 1990-06-15T00:00:00Z
    """
    if not date_str:
        return None
    try:
        # Handle 2009-11-19 00:00:00.0
        if " " in date_str:
            dt = datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        else:
            # Handle 1990-06-15
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return date_str

def map_nid_to_spdci(data):
    """
    Maps NID response structure to standardized Group/SPDCI structure.
    """
    # Extract identifiers
    nin = data.get("nin_loc", "")
    cc_number = data.get("cc_number_loc", "")
    
    # Format dates
    dob_iso = format_date_to_iso(data.get("dob", ""))
    cc_issuing_date_iso = format_date_to_iso(data.get("cc_issuing_date", ""))
    
    # Gender mapping
    gender = data.get("gender", "")
    sex = "female" if gender == "F" else "male" if gender == "M" else gender
    
    # Address helpers
    street_address = f"{data.get('perm_village_tol', '')}, Ward {data.get('perm_ward', '')}"
    city = f"Municipality {data.get('perm_rur_mun', '')}, District {data.get('perm_district', '')}"
    postal_code = str(data.get("perm_rur_mun", ""))
    
    # portrait image handling
    portrait_image = data.get("portrait_image", "")
    if portrait_image and not portrait_image.startswith("base64:"):
        portrait_base64 = f"base64:{portrait_image}"
    else:
        portrait_base64 = portrait_image

    result = {
        "@type": "Group",
        "group_identifier": [
            {
                "identifier_type": "NationalID",
                "identifier_value": nin
            }
        ],
        "group_type": "family",
        "place": {
            "@type": "Place",
            "geo": { "@type": "spdci:GeoLocation", "latitude": 0, "longitude": 0 },
            "address": {
                "@type": "Address",
                "street_address": street_address,
                "city": city,
                "postal_code": postal_code,
                "country": "Nepal"
            }
        },
        "poverty_score": None,
        "poverty_score_type": None,
        "group_head_info": {
            "@type": "Member",
            "member_identifier": [
                { "identifier_type": "NationalID", "identifier_value": nin }
            ],
            "demographic_info": {
                "@type": "SRPerson",
                "identifier": [
                    { "identifier_type": "NationalID", "identifier_value": nin },
                    { "identifier_type": "CitizenshipCertificate", "identifier_value": cc_number }
                ],
                "name": {
                    "given_name": data.get("first_name", ""),
                    "surname": data.get("last_name", ""),
                    "prefix": "",
                    "suffix": ""
                },
                "sex": sex,
                "birth_date": dob_iso,
                "address": {
                    "@type": "Address",
                    "street_address": street_address,
                    "city": city,
                    "postal_code": postal_code,
                    "country": "Nepal"
                },
                "registration_date": cc_issuing_date_iso
            },
            "is_disabled": False,
            "marital_status": "",
            "registration_date": cc_issuing_date_iso
        },
        "group_size": 1,
        "member_list": [],
        "registration_date": cc_issuing_date_iso,
        "last_updated": cc_issuing_date_iso,
        "additional_attributes": [
            { "key": "name_local", "value": f"{data.get('first_name_loc', '')} {data.get('last_name_loc', '')}".strip() },
            { "key": "dob_local", "value": data.get("dob_loc", "") },
            { "key": "nin_local", "value": nin },
            { "key": "father_name", "value": f"{data.get('f_first_name', '')} {data.get('f_last_name', '')}".strip() },
            { "key": "father_name_local", "value": f"{data.get('f_first_name_loc', '')} {data.get('f_last_name_loc', '')}".strip() },
            { "key": "mother_name", "value": f"{data.get('m_first_name', '')} {data.get('m_last_name', '')}".strip() },
            { "key": "mother_name_local", "value": f"{data.get('m_first_name_loc', '')} {data.get('m_last_name_loc', '')}".strip() },
            { "key": "grandfather_name", "value": f"{data.get('gf_first_name', '')} {data.get('gf_last_name', '')}".strip() },
            { "key": "grandfather_name_local", "value": f"{data.get('gf_first_name_loc', '')} {data.get('gf_last_name_loc', '')}".strip() },
            { "key": "cc_number_local", "value": cc_number },
            { "key": "cc_issuing_district", "value": str(data.get("cc_issuing_district", "")) },
            { "key": "cc_issuing_date", "value": (data.get("cc_issuing_date") or "").split(" ")[0] },
            { "key": "cc_issuing_date_local", "value": data.get("cc_issuing_date_loc", "") },
            { "key": "perm_state", "value": str(data.get("perm_state", "")) },
            { "key": "perm_district", "value": str(data.get("perm_district", "")) },
            { "key": "perm_rur_mun", "value": str(data.get("perm_rur_mun", "")) },
            { "key": "perm_ward", "value": str(data.get("perm_ward", "")) },
            { "key": "perm_village_tol", "value": data.get("perm_village_tol", "") },
            { "key": "perm_address_local", "value": f"{data.get('perm_village_tol_loc', '')}, वडा {data.get('perm_ward_loc', '')}".strip() },
            { "key": "portrait_image", "value": portrait_base64 }
        ]
    }
    return result
