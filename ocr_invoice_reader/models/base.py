"""
Base data models for document extraction
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import json
import csv
from pathlib import Path


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

    def to_csv_row(self) -> Dict[str, Any]:
        """Convert document to a single CSV row (flat structure)"""
        return {
            'document_type': self.document_type,
            'document_number': self.document_number or '',
            'date': self.date or '',
            'sender_company': self.sender.company if self.sender else '',
            'sender_address': self.sender.address if self.sender else '',
            'sender_phone': self.sender.phone if self.sender else '',
            'sender_contact': self.sender.contact if self.sender else '',
            'receiver_company': self.receiver.company if self.receiver else '',
            'receiver_address': self.receiver.address if self.receiver else '',
            'receiver_phone': self.receiver.phone if self.receiver else '',
            'receiver_contact': self.receiver.contact if self.receiver else '',
            'item_count': len(self.items),
            'subtotal': self.subtotal or '',
            'tax': self.tax or '',
            'total_amount': self.total_amount or '',
            'currency': self.currency,
            'notes': self.notes or '',
            'reference': self.reference or '',
            'confidence': f"{self.confidence:.2%}",
            'extraction_method': self.extraction_method,
            'source_file': self.source_file or ''
        }

    def to_csv_items(self) -> List[Dict[str, Any]]:
        """Convert document items to CSV rows (one row per item)"""
        rows = []
        for idx, item in enumerate(self.items, 1):
            rows.append({
                'document_number': self.document_number or '',
                'document_type': self.document_type,
                'item_index': idx,
                'description': item.description,
                'quantity': item.quantity or '',
                'unit': item.unit or '',
                'unit_price': item.unit_price or '',
                'amount': item.amount or '',
                'notes': item.notes or '',
                'source_file': self.source_file or ''
            })
        return rows

    def save_to_csv(self, file_path: str, mode: str = 'summary'):
        """
        Save document to CSV file

        Args:
            file_path: Output CSV file path
            mode: 'summary' (one row per document) or 'items' (one row per item)
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if mode == 'summary':
            rows = [self.to_csv_row()]
            if rows:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
        elif mode == 'items':
            rows = self.to_csv_items()
            if rows:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'summary' or 'items'")

    @staticmethod
    def save_multiple_to_csv(documents: List['BaseDocument'], file_path: str, mode: str = 'summary'):
        """
        Save multiple documents to a single CSV file

        Args:
            documents: List of documents to save
            file_path: Output CSV file path
            mode: 'summary' (one row per document) or 'items' (one row per item)
        """
        if not documents:
            return

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if mode == 'summary':
            rows = [doc.to_csv_row() for doc in documents]
        elif mode == 'items':
            rows = []
            for doc in documents:
                rows.extend(doc.to_csv_items())
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'summary' or 'items'")

        if rows:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
