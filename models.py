from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union

class Customer(BaseModel):
    id: str
    type: str
    customerId: str
    title: str
    firstName: str
    lastName: str
    emailAddress: str
    phoneNumber: str
    creationDate: str
    addresses: List
    password: Dict
    salesOrderCount: int
    rid: Optional[str] = Field(alias="_rid")
    self: Optional[str] = Field(alias="_self")
    etag: Optional[str] = Field(alias="_etag")
    attachments: Optional[str] = Field(alias="_attachments")
    ts: Optional[int] = Field(alias="_ts")

class Product(BaseModel):
    id: str
    categoryId: str
    categoryName: str
    sku: str
    name: str
    description: str
    price: float
    tags: List[Dict[str, str]]

class SalesOrder(BaseModel):
    id: str 
    type: str
    customerId: str
    orderDate: str
    shipDate: str
    details: List[Dict[str, Union[str, float, int]]]
    rid: Optional[str] = Field(alias="_rid")
    self: Optional[str] = Field(alias="_self")
    etag: Optional[str] = Field(alias="_etag")
    attachments: Optional[str] = Field(alias="_attachments")
    ts: Optional[int] = Field(alias="_ts")

