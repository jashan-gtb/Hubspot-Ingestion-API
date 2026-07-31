from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="B2B Lead Pipline Ingestion API")

HUBSPOT_TOKKEN = os.getenv("tokken")

HUBSPOT_URL = "https://api.hubapi.com/crm/v3/objects/companies"


class LeadPayLoad(BaseModel):
    name: str
    phone: Optional[str] = "NA"
    city: Optional[str] = "NA"
    domain: str
    email: Optional[str] = "NA"
    seo_flaws: List[str]
    score: float


@app.post("/api/v1/leads/ingest")
async def injest_lead(payload: LeadPayLoad):

    print("\n" + "=" * 40)
    print(f"NEW QUALIFIED LEAD RECEIVED!")
    print(f"Company: {payload.name}")
    print(f"Phone: {payload.phone}")
    print(f"Website: {payload.domain}")
    print(f"Email: {payload.email}")
    print("SEO Flaws Identified for Sales Pitch:")

    for flaw in payload.seo_flaws:
        print(f"  ❌ {flaw}")

    print("SEO Flaws score: ", payload.score)

    print("=" * 40 + "\n")

    flaw_string = ", ".join(payload.seo_flaws)

    properties = {
        "name": payload.name,
        "domain": payload.domain,
        "description": f"SEO Audit failed-\nSEO Flaw Score: {payload.score}\nFlaws: {flaw_string}",
    }

    if payload.phone and payload.phone not in ["NA", "N/A"]:
        properties["phone"] = payload.phone

    if payload.email and payload.email not in ["NA", "N/A"]:
        properties["email"] = payload.email

    if payload.city and payload.city not in ["NA", "N/A"]:
        properties["city"] = payload.city

    hubspot_data = {"properties": properties}

    HEADERS = {
        "Authorization": f"Bearer {HUBSPOT_TOKKEN}",
        "Content-Type": "application/json",
    }

    # to remove duplicates

    search_url = "https://api.hubapi.com/crm/v3/objects/companies/search"

    search_payload = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "domain",
                        "operator": "EQ",
                        "value": payload.domain,
                    }
                ]
            }
        ]
    }

    search_response = requests.post(search_url, headers=HEADERS, json=search_payload)
    search_result = search_response.json()

    if search_result.get("total", 0) > 0:
        print(f"⚠️ {payload.name} already exists in HubSpot CRM (Skipped).")
        print("=" * 40 + "\n")
        return {"Status": "Skipped", "message": "Lead already exists in CRM"}

    response_post = requests.post(HUBSPOT_URL, headers=HEADERS, json=hubspot_data)

    if response_post.status_code in [200, 201]:
        print("Successfully injected into HubSpot CRM!")
        return {"Status": "Success", "message": "Lead Injected to Hubspot"}

    else:
        print(f"❌ HubSpot Rejected Payload: {response_post.text}")
        raise HTTPException(
            status_code=response_post.status_code, detail=response_post.json()
        )
