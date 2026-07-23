# LeadFlow HubSpot Ingestion API

A FastAPI service that receives qualified B2B leads, captures their SEO audit findings, and creates company records in HubSpot CRM. It is designed as a lightweight integration point between a lead-generation or scraping workflow and a sales pipeline.

## What it does

- Accepts lead details and a list of SEO issues through a REST endpoint.
- Prints a clear lead summary to the application log for visibility during development.
- Maps the lead to a HubSpot Company object.
- Stores the SEO findings in the company description to give sales teams immediate context.
- Returns a friendly result for successful submissions and duplicate companies.

## Tech stack

- Python
- FastAPI and Pydantic
- Requests
- HubSpot CRM API

## Prerequisites

- Python 3.10 or later
- A HubSpot private-app access token with permission to create company records

## Installation

Clone the repository and move into the API directory:

```bash
git clone <your-repository-url>
cd Api-Receiver
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\\Scripts\\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Set your HubSpot private-app token in an environment variable named `tokken` (the application currently uses this exact spelling):

```bash
export tokken="your_hubspot_private_app_token"
```

On Windows PowerShell:

```powershell
$env:tokken="your_hubspot_private_app_token"
```

Never commit private-app tokens to source control. For local development, you can store the value in your shell profile or secret manager.

## Run the API

From the `Api-Receiver` directory, start the development server:

```bash
uvicorn receiver:app --reload
```

The service will be available at `http://127.0.0.1:8000`. FastAPI’s interactive API documentation is available at `http://127.0.0.1:8000/docs`.

## API reference

### `POST /api/v1/leads/ingest`

Receives a qualified lead and sends it to HubSpot as a company record.

#### Request body

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | Yes | Company name. |
| `domain` | string | Yes | Company website domain. |
| `seo_flaws` | array of strings | Yes | SEO issues identified during the audit. |
| `phone` | string | No | Company phone number. Defaults to `"NA"`. |
| `city` | string | No | Company city. Defaults to `"NA"`. |
| `email` | string | No | Company email address. Defaults to `"NA"`. |

#### Example request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/leads/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme HVAC",
    "domain": "acmehvac.com",
    "phone": "+1-480-555-0142",
    "city": "Scottsdale",
    "email": "hello@acmehvac.com",
    "seo_flaws": [
      "Missing meta descriptions on service pages",
      "Slow mobile page speed",
      "No local business schema"
    ]
  }'
```

#### Success response

```json
{
  "Status": "Success",
  "message": "Lead Injected to Hubspot"
}
```

If HubSpot reports that the company already exists, the API responds with:

```json
{
  "Status": "Skipped",
  "message": "Lead already exists in CRM"
}
```

## HubSpot field mapping

| API field | HubSpot company property |
| --- | --- |
| `name` | `name` |
| `domain` | `domain` |
| `phone` | `phone` when supplied |
| `email` | `email` when supplied |
| `city` | `city` when supplied |
| `seo_flaws` | Combined into the `description` field |

## Project structure

```text
Api-Receiver/
├── receiver.py        # FastAPI application and HubSpot integration
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

## License

Add a license file before publishing if you want to specify how others may use this project.
