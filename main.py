import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Product as ProductSchema, Lead as LeadSchema

app = FastAPI(title="Jay Beny Trading Co API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Jay Beny Trading Co Backend Running"}


@app.get("/api/info")
def company_info():
    return {
        "name": "Jay Beny Trading Co",
        "tagline": "Cement • TMT Rebar • All Building Materials",
        "location": "Gossainpur, Bagdogra",
        "phones": ["9800014161", "9832030002"],
        "whatsapp": "9800014161",
        "services": [
            "Retail & wholesale supply",
            "On-site delivery",
            "Bulk orders for projects",
        ],
        "categories": [
            "Cement",
            "TMT Rebar",
            "Bricks & Blocks",
            "Sand & Aggregates",
            "Binding Wire & Nails",
            "Pipes & Fittings",
        ],
    }


@app.get("/api/products", response_model=List[ProductSchema])
def list_products():
    try:
        # If no products, seed with some defaults
        count = db["product"].count_documents({}) if db else 0
        if count == 0 and db is not None:
            samples = [
                {
                    "name": "Ordinary Portland Cement (OPC 43)",
                    "category": "Cement",
                    "brand": "UltraTech",
                    "grade": "OPC 43",
                    "unit": "bag",
                    "price_per_unit": 0,
                    "in_stock": True,
                    "description": "Fresh stock, best rates for bulk orders",
                },
                {
                    "name": "Portland Pozzolana Cement (PPC)",
                    "category": "Cement",
                    "brand": "Dalmia",
                    "grade": "PPC",
                    "unit": "bag",
                    "price_per_unit": 0,
                    "in_stock": True,
                    "description": "Ideal for general construction",
                },
                {
                    "name": "TMT Rebar 12mm Fe500D",
                    "category": "TMT Rebar",
                    "brand": "SRMB",
                    "grade": "Fe500D",
                    "unit": "piece",
                    "price_per_unit": 0,
                    "in_stock": True,
                    "description": "High strength ductile rebar",
                },
                {
                    "name": "Coarse Sand",
                    "category": "Sand & Aggregates",
                    "brand": None,
                    "grade": None,
                    "unit": "cubic ft",
                    "price_per_unit": 0,
                    "in_stock": True,
                    "description": "Clean, screened coarse sand",
                },
            ]
            for s in samples:
                try:
                    p = ProductSchema(**s)
                    create_document("product", p)
                except Exception:
                    pass

        docs = get_documents("product") if db is not None else []
        # Convert ObjectId and other non-serializable fields
        cleaned = []
        for d in docs:
            d.pop("_id", None)
            d.pop("created_at", None)
            d.pop("updated_at", None)
            try:
                cleaned.append(ProductSchema(**d))
            except ValidationError:
                # skip invalid doc
                continue
        return cleaned
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LeadResponse(BaseModel):
    success: bool
    message: str
    id: Optional[str] = None


@app.post("/api/leads", response_model=LeadResponse)
def create_lead(lead: LeadSchema):
    try:
        inserted_id = create_document("lead", lead)
        return LeadResponse(success=True, message="Enquiry submitted. We'll reach out shortly.", id=inserted_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
