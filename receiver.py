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

    print("=" * 40 + "\n")

    flaw_string = ", ".join(payload.seo_flaws)

    properties = {
        "name": payload.name,
        "domain": payload.domain,
        "description": f"SEO Audit failed. Flaws: {flaw_string}",
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

    response = requests.post(HUBSPOT_URL, json=hubspot_data, headers=HEADERS)

    if response.status_code in [200, 201]:
        print("Successfully injected into HubSpot CRM!")
        return {"Status": "Success", "message": "Lead Injected to Hubspot"}

    elif response.status_code == 409:
        print("Lead already exists in HubSpot CRM (Skipped).")
        return {"Status": "Skipped", "message": "Lead already exists in CRM"}

    else:
        print(f"❌ HubSpot Rejected Payload: {response.text}")
        raise HTTPException(status_code=response.status_code, detail=response.json())
