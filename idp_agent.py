import os
import sys
import json
import mimetypes
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# --- Pydantic Data Schemas for Gemini API (No Dicts to avoid additionalProperties errors) ---

class KeyValuePair(BaseModel):
    key: str = Field(description="Name of the key or property")
    value: str = Field(description="Value of the key or property")

class RowDetail(BaseModel):
    column_name: str = Field(description="Header name of the column (e.g., Description, Quantity, Unit Price, Total)")
    value: str = Field(description="Value in this column for this row")

class DocumentMetadata(BaseModel):
    document_type: str = Field(description="Type of document (e.g., Invoice, Legal Contract, Identification/Passport, Bank Statement, Medical Report, Academic Paper, Receipt, Unknown)")
    language: str = Field(description="Detected language of the document")
    page_count: Optional[int] = Field(None, description="Number of pages or null")
    classification_confidence: float = Field(description="Confidence score for classification between 0.0 and 1.0")

class Identifiers(BaseModel):
    document_number: Optional[str] = Field(None, description="Unique document ID (Invoice #, Contract #, Tax ID, etc.) or null")
    reference_numbers: List[str] = Field(default_factory=list, description="List of other reference numbers found")

class DatesAPI(BaseModel):
    issue_date: Optional[str] = Field(None, description="Issue date in YYYY-MM-DD or original format, or null")
    expiry_date: Optional[str] = Field(None, description="Expiry date or null")
    other_relevant_dates: List[KeyValuePair] = Field(default_factory=list, description="Other relevant dates found as key-value pairs")

class Parties(BaseModel):
    issuer_or_sender: Optional[str] = Field(None, description="Issuer or sender of the document, or null")
    recipient_or_buyer: Optional[str] = Field(None, description="Recipient or buyer of the document, or null")
    signatories: List[str] = Field(default_factory=list, description="Signatories mentioned in the document")

class Financials(BaseModel):
    currency: Optional[str] = Field(None, description="Currency (ISO code if possible) or null")
    subtotal: Optional[float] = Field(None, description="Subtotal amount or null")
    tax_amount: Optional[float] = Field(None, description="Tax amount or null")
    total_amount: Optional[float] = Field(None, description="Total amount or null")

class ExtractedDataAPI(BaseModel):
    identifiers: Identifiers
    dates: DatesAPI
    parties: Parties
    financials: Financials

class RowItemAPI(BaseModel):
    item_index: int
    details: List[RowDetail] = Field(description="List of column details/values for this row")

class TableOrListAPI(BaseModel):
    table_name: str = Field(description="Name of the table (e.g., Line Items)")
    headers: List[str] = Field(description="List of column headers")
    rows: List[RowItemAPI] = Field(description="List of row objects")

class ValidationFlags(BaseModel):
    has_signature: bool = Field(description="Whether a signature is present in the document")
    has_stamp_or_seal: bool = Field(description="Whether a stamp or seal is present in the document")
    potential_anomalies: List[str] = Field(default_factory=list, description="Potential issues, alterations, or incomplete sections")
    extraction_confidence_score: float = Field(description="Overall confidence score for extraction between 0.0 and 1.0")

class DocumentAnalysisAPI(BaseModel):
    metadata: DocumentMetadata
    extracted_data: ExtractedDataAPI
    tables_and_lists: List[TableOrListAPI]
    validation_and_flags: ValidationFlags
    semantic_summary: str = Field(description="Concise 2-3 sentence summary of the document’s purpose and current legal/financial status")

class TopLevelResponseAPI(BaseModel):
    document_analysis: Optional[DocumentAnalysisAPI] = Field(None, description="Detailed document analysis if readable")
    error: Optional[str] = Field(None, description="Set to 'UNREADABLE_DOCUMENT' if the input file is blank, corrupted, or completely unreadable")
    message: Optional[str] = Field(None, description="Error explanation message if unreadable")

# --- Helper Functions ---

def print_error(message: str, error_code: str = "UNREADABLE_DOCUMENT"):
    print(json.dumps({
        "error": error_code,
        "message": message
    }, indent=2))
    sys.exit(0)

def transform_to_expected_schema(response_dict: dict) -> dict:
    """Transform structured List fields back into dicts to match the expected JSON output format."""
    if not response_dict or "document_analysis" not in response_dict:
        return response_dict

    analysis = response_dict["document_analysis"]
    if not analysis:
        return response_dict

    # 1. Transform dates.other_relevant_dates from list of {key, value} to dict
    extracted_data = analysis.get("extracted_data", {})
    dates = extracted_data.get("dates", {})
    if isinstance(dates.get("other_relevant_dates"), list):
        dates["other_relevant_dates"] = {
            item["key"]: item["value"]
            for item in dates["other_relevant_dates"]
            if isinstance(item, dict) and "key" in item and "value" in item
        }

    # 2. Transform tables_and_lists rows details from list of {column_name, value} to dict
    tables = analysis.get("tables_and_lists", [])
    if isinstance(tables, list):
        for table in tables:
            rows = table.get("rows", [])
            if isinstance(rows, list):
                for row in rows:
                    details_list = row.get("details", [])
                    if isinstance(details_list, list):
                        row["details"] = {
                            item["column_name"]: item["value"]
                            for item in details_list
                            if isinstance(item, dict) and "column_name" in item and "value" in item
                        }
                        
    return response_dict

# --- Main Logic ---

def main():
    if len(sys.argv) < 2:
        print_error("No input file path provided. Usage: python idp_agent.py <file_path>", "INVALID_ARGUMENTS")

    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}", "UNREADABLE_DOCUMENT")

    if os.path.getsize(file_path) == 0:
        print_error("The document provided could not be processed or contains no legible text/data.", "UNREADABLE_DOCUMENT")

    # Read file bytes
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
    except Exception as e:
        print_error(f"Failed to read file: {str(e)}", "UNREADABLE_DOCUMENT")

    # Guess MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        if file_path.lower().endswith(".pdf"):
            mime_type = "application/pdf"
        elif file_path.lower().endswith(".png"):
            mime_type = "image/png"
        elif file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg"):
            mime_type = "image/jpeg"
        else:
            mime_type = "application/octet-stream"

    # Initialize Gemini client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("GEMINI_API_KEY environment variable is not set.", "API_KEY_MISSING")

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = (
            "Analyze this document. Ingest, analyze, categorize, and extract structured information. "
            "If the document is blank, corrupted, or completely unreadable, set error to 'UNREADABLE_DOCUMENT' "
            "and message to 'The document provided could not be processed or contains no legible text/data.'. "
            "For confidence scoring, provide a score between 0.0 and 1.0. For missing fields, set to null."
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type,
                ),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TopLevelResponseAPI,
            ),
        )
        
        # Output directly to stdout
        if response.text:
            parsed = json.loads(response.text)
            transformed = transform_to_expected_schema(parsed)
            # Pop null keys to strictly match schema formats
            if transformed.get("document_analysis") is not None:
                transformed.pop("error", None)
                transformed.pop("message", None)
            else:
                transformed.pop("document_analysis", None)
            print(json.dumps(transformed, indent=2))
        else:
            print_error("Empty response from AI model.", "UNREADABLE_DOCUMENT")

    except Exception as e:
        print_error(f"Model generation error: {str(e)}", "UNREADABLE_DOCUMENT")

if __name__ == "__main__":
    main()
