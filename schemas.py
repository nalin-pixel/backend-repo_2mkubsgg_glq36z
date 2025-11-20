"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- Lead -> "lead" collection
"""

from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    """
    Building Materials product schema
    Collection name: "product"
    """
    name: str = Field(..., description="Product name, e.g., Ultratech Cement, TMT 12mm")
    category: str = Field(..., description="Category like Cement, TMT Rebar, Sand, Bricks, Aggregates, Others")
    brand: Optional[str] = Field(None, description="Brand name if applicable")
    grade: Optional[str] = Field(None, description="Grade or spec, e.g., OPC 43, Fe500D")
    unit: str = Field(..., description="Selling unit, e.g., bag, piece, ton, cubic ft, bundle")
    price_per_unit: Optional[float] = Field(None, ge=0, description="Indicative price per unit")
    in_stock: bool = Field(True, description="Whether available for delivery")
    description: Optional[str] = Field(None, description="Short description or notes")

class Lead(BaseModel):
    """
    Sales enquiry lead schema
    Collection name: "lead"
    """
    name: str = Field(..., description="Customer name")
    phone: str = Field(..., description="Contact number")
    requirement: Optional[str] = Field(None, description="Required material or category")
    quantity: Optional[str] = Field(None, description="Approx quantity, e.g., 50 bags, 2 tons")
    location: Optional[str] = Field(None, description="Site location or delivery address area")
    message: Optional[str] = Field(None, description="Additional notes")

# (Optional) Keep a lightweight user model for future expansion
class User(BaseModel):
    name: str
    phone: Optional[str] = None
    is_active: bool = True
