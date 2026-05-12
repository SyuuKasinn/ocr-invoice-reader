"""
Base data models for document extraction
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import json


class Address(BaseModel):
    """Address information"""
    company: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None

    def is_empty(self) -> bool:
        """Check if address is empty"""
        return all(v is None for v in self.model_dump().values())

    def __str__(self) -> str:
        parts = []
        if self.company:
            parts.append(f"Company: {self.company}")
        if self.address:
            parts.append(f"Address: {self.address}")
        if self.phone:
            parts.append(f"Phone: {self.phone}")
        if self.contact:
            parts.append(f"Contact: {self.contact}")
        return "\n".join(parts) if parts else "Empty Address"


class DocumentItem(BaseModel):
    """Document item (for invoices, orders, etc.)"""
    description: str = Field(..., description="Item description")
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    notes: Optional[str] = None

    def __str__(self) -> str:
        parts = [f"Item: {self.description}"]
        if self.quantity:
            unit = f" {self.unit}" if self.unit else ""
            parts.append(f"Qty: {self.quantity}{unit}")
        if self.unit_price:
            parts.append(f"Price: {self.unit_price}")
        if self.amount:
            parts.append(f"Amount: {self.amount}")
        return ", ".join(parts)


class BaseDocument(BaseModel):
    """Base document model"""
    # Document type
    document_type: str = Field("unknown", description="invoice/waybill/contract/other")

    # Basic information
    document_number: Optional[str] = Field(None, description="Document number (invoice/tracking)")
    date: Optional[str] = Field(None, description="Document date (YYYY-MM-DD)")

    # Sender/Shipper
    sender: Optional[Address] = None

    # Receiver/Consignee
    receiver: Optional[Address] = None

    # Items/Products
    items: List[DocumentItem] = []

    # Financial information
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    currency: str = "JPY"

    # Additional information
    notes: Optional[str] = None
    reference: Optional[str] = None

    # Metadata
    confidence: float = Field(0.0, description="Extraction confidence (0-1)")
    extraction_method: str = Field("unknown", description="Extraction method used")
    extraction_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    source_file: Optional[str] = None

    # Raw OCR data (for debugging)
    raw_ocr_results: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return self.model_dump_json(indent=indent, exclude_none=True)

    def save_to_file(self, file_path: str):
        """Save to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def from_json_file(cls, file_path: str):
        """Load from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

    def __str__(self) -> str:
        """String representation"""
        lines = []
        lines.append(f"Document Type: {self.document_type}")

        if self.document_number:
            lines.append(f"Number: {self.document_number}")
        if self.date:
            lines.append(f"Date: {self.date}")

        if self.sender and not self.sender.is_empty():
            lines.append(f"\nSender:")
            lines.append(str(self.sender))

        if self.receiver and not self.receiver.is_empty():
            lines.append(f"\nReceiver:")
            lines.append(str(self.receiver))

        if self.items:
            lines.append(f"\nItems ({len(self.items)}):")
            for i, item in enumerate(self.items, 1):
                lines.append(f"  {i}. {item}")

        if self.total_amount:
            lines.append(f"\nTotal: {self.total_amount} {self.currency}")

        lines.append(f"\nConfidence: {self.confidence:.2%}")
        lines.append(f"Method: {self.extraction_method}")

        return "\n".join(lines)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        return {
            "document_type": self.document_type,
            "document_number": self.document_number,
            "date": self.date,
            "sender_company": self.sender.company if self.sender else None,
            "receiver_company": self.receiver.company if self.receiver else None,
            "item_count": len(self.items),
            "total_amount": self.total_amount,
            "currency": self.currency,
            "confidence": self.confidence,
            "method": self.extraction_method
        }
