"""AI service for document extraction and commodity group suggestion."""

import json
from typing import List
from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.constants import COMMODITY_GROUPS, DEPARTMENTS
from app.models.request import OrderLine
from app.models.metadata import DocumentExtractionResponse, CommodityGroupSuggestion


class AIService:
    """Service for AI-powered features."""

    def __init__(self):
        """Initialize OpenAI client if API key is available."""
        self.client = None
        if OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.client is not None

    async def extract_document(self, text_content: str) -> DocumentExtractionResponse:
        """Extract information from vendor offer document."""
        if not self.client:
            raise ValueError("OpenAI client not initialized")

        # Build commodity groups reference for the AI
        cg_reference = "\n".join(
            [f"- {g['id']}: {g['category']} > {g['name']}" for g in COMMODITY_GROUPS]
        )

        # Build departments reference
        dept_reference = ", ".join(DEPARTMENTS)

        extraction_prompt = f"""You are an expert at extracting structured information from German vendor offer documents (Angebote).

TASK: Extract information from this vendor offer document.

## EXTRACTION RULES

### 1. Requestor Name
Find the PERSON or COMPANY NAME the offer is addressed to. Look for:
- The recipient company name in the address block (e.g., "Lio Technologies GmbH")
- A person's name like "Vladimir Keil" or "Herr/Frau [Name]"
- Use the company name if no person name is found

### 2. Title
Generate a SHORT title (max 50 chars) describing the main purchase. Examples:
- "Moosbild mit Logointegration" (for moss picture with logo)
- "MacBook Air M2" (for laptop)
- "Büromöbel" (for office furniture)

### 3. Vendor Name  
The company SENDING the offer (not the recipient). Look for:
- Company name in letterhead at top
- Company name in footer
- Company name before address (e.g., "Dream in Green GmbH", "styleGREEN", "FlowerArt GmbH")

### 4. VAT ID (CRITICAL - DO NOT INVENT)
Vendor's VAT number. Look for these exact patterns:
- "USt.-ID:" or "USt-IdNr:" or "Ust.-Id.:" followed by the number
- "Steuer-Nr:" or "Steuernummer:"
- Format: Usually "DE" followed by 9 digits (e.g., DE325240530)

**IMPORTANT**: If you cannot find a VAT ID in the document, return null. NEVER invent or guess a VAT ID like "DE123456789".

### 5. Department
Select the most appropriate department from this list based on the nature of the purchase:
{dept_reference}
For example: IT equipment → "IT", office furniture → "Administration", marketing materials → "Marketing", etc.
If unclear, use "Procurement" as the default.

### 6. Order Lines - CRITICAL RULES:
- Extract ONLY products/services from the line items table (Pos. 1, 2, 3, etc.)
- INCLUDE shipping costs (Versandkosten) as a separate order line
- NEVER include tax lines (USt., MwSt., Umsatzsteuer) as order lines
- Use EXACT quantities from document - can be decimals (1.28, 4.80, etc.)
- Use the EXACT unit from document (qm, Lfm, Stk., Stück, etc.)

**SKIP ALTERNATIVE ITEMS:**
- Items marked "Alternativ:", "Alt.", or "(Alt.)" are alternatives, NOT additional items
- Only include ONE of the alternatives (the main one, not the alternative)
- Example: If you see "Logointegration horizontal" and "Alternativ: Logo vertikal", only include the horizontal one

**SKIP DUPLICATE/HEADER ROWS:**
- Some documents list an item twice (once as header, once with price)
- Only extract lines that have BOTH a price AND a "Gesamt €" value
- Skip lines that are just descriptions without prices

**PRICE EXTRACTION - CRITICAL:**
- Use the "Gesamt €" column value as total_price
- For unit_price: use total_price ÷ amount
- If there's a discount (Rabatt), the "Gesamt €" already reflects the discounted price

**HANDLING DISCOUNTS:**
- If a line shows "Rabatt -20%" with original price 894,08 € and Gesamt 715,26 €:
  - unit_price = 715.26 (the FINAL discounted price, since amount is 1)
  - total_price = 715.26
- The unit_price × amount MUST equal total_price

**Example with discount:**
| Pos | Description | Menge | Preis/Einh € | Rabatt | Gesamt € |
| 2   | Moosbild    | 1.00  | 894,08       | -20%   | 715,26   |

Extract as:
- unit_price: 715.26 (NOT 894.08)
- amount: 1.00
- total_price: 715.26

**Example without discount:**
| Pos | Description | Menge | Einheit | Preis/Einh € | Gesamt € |
| 1   | Product     | 1.28  | qm      | 559,00       | 715,52   |

Extract as:
- unit_price: 559.00
- amount: 1.28  
- total_price: 715.52

### 7. Total Cost
Use the "Endsumme" or "Gesamtsumme" - the final amount INCLUDING all taxes.
This is the amount the customer will actually pay.
Note: The frontend will automatically calculate and add a VAT line if needed.

### 8. Commodity Group Selection
For moss pictures, green walls, office decoration, interior plants:
- Use "015" (Office Equipment) under Facility Management
For promotional items with company logos:
- Use "043" (Promotional Materials) under Marketing & Advertising

## AVAILABLE COMMODITY GROUPS:
{cg_reference}

## DOCUMENT CONTENT:
---
{text_content}
---

## RESPONSE FORMAT (JSON):
{{
    "requestor_name": "string or null",
    "title": "string - short description of purchase",
    "vendor_name": "string or null", 
    "vat_id": "string or null (ONLY if found in document, never invent)",
    "department": "string - one of the predefined departments, or null",
    "order_lines": [
        {{
            "description": "product/service name",
            "unit_price": number (EXACT price per unit from document),
            "amount": number (EXACT quantity, can be decimal like 1.28),
            "unit": "string (exact unit from document: qm, Lfm, Stk., etc.)",
            "total_price": number (EXACT line total from document)
        }}
    ],
    "total_cost": number (Endsumme/Gesamtsumme INCLUDING tax),
    "suggested_commodity_group_id": "3-digit string or null",
    "suggested_commodity_group_name": "string or null",
    "extraction_confidence": number 0-1
}}

## VALIDATION CHECKLIST:
✓ VAT ID is either found in document OR null (never invented)
✓ For each line: unit_price × amount = total_price (within 0.01 tolerance)
✓ No tax lines in order_lines
✓ No alternative items (marked "Alternativ" or "Alt.")
✓ Quantities are exact (decimals preserved: 1.28, 4.80)
✓ German number format converted: 1.337,26 → 1337.26
✓ total_cost is the Endsumme (final amount with tax)
✓ Sum of order line totals + shipping ≈ "Positionen netto" + "Versandkosten netto"
"""

        try:
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise document extraction assistant. Always respond with valid JSON only.",
                    },
                    {"role": "user", "content": extraction_prompt},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            # Validate and transform order lines
            order_lines = []
            for line in result.get("order_lines", []):
                order_lines.append(
                    OrderLine(
                        description=line.get("description", ""),
                        unit_price=float(line.get("unit_price", 0)),
                        amount=float(
                            line.get("amount", 1)
                        ),  # Support decimal quantities
                        unit=line.get("unit", "units"),
                        total_price=float(line.get("total_price", 0)),
                    )
                )

            return DocumentExtractionResponse(
                requestor_name=result.get("requestor_name"),
                title=result.get("title"),
                vendor_name=result.get("vendor_name"),
                vat_id=result.get("vat_id"),
                department=result.get("department"),
                order_lines=order_lines,
                total_cost=result.get("total_cost"),
                suggested_commodity_group_id=result.get("suggested_commodity_group_id"),
                suggested_commodity_group_name=result.get(
                    "suggested_commodity_group_name"
                ),
                extraction_confidence=result.get("extraction_confidence", 0.8),
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Document extraction failed: {str(e)}")

    async def suggest_commodity_group(
        self, title: str, order_lines: List[dict]
    ) -> CommodityGroupSuggestion:
        """Suggest the best commodity group based on request title and order lines."""
        if not self.client:
            raise ValueError("OpenAI client not initialized")

        # Build commodity groups reference
        cg_reference = "\n".join(
            [f"- {g['id']}: {g['category']} > {g['name']}" for g in COMMODITY_GROUPS]
        )

        # Build order lines description
        lines_desc = "\n".join(
            [f"- {line.get('description', 'Unknown')}" for line in order_lines]
        )

        suggestion_prompt = f"""You are an expert procurement specialist. Based on the request title and items, suggest the most appropriate commodity group.

Request Title: {title}

Items/Services:
{lines_desc if lines_desc else "Not specified"}

Available Commodity Groups:
{cg_reference}

Analyze the request and select the SINGLE most appropriate commodity group. Consider:
- The nature of the products/services being requested
- The category that best fits the items
- Common procurement classifications

Respond in JSON format:
{{
    "commodity_group_id": "string (3-digit ID)",
    "commodity_group_name": "string",
    "category": "string",
    "confidence": number between 0 and 1,
    "reasoning": "brief explanation of why this commodity group was selected"
}}
"""

        try:
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a procurement classification expert. Always respond with valid JSON only.",
                    },
                    {"role": "user", "content": suggestion_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)

            return CommodityGroupSuggestion(
                commodity_group_id=result.get("commodity_group_id", "009"),
                commodity_group_name=result.get(
                    "commodity_group_name", "Miscellaneous Services"
                ),
                category=result.get("category", "General Services"),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", "Default classification"),
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            raise ValueError(f"Commodity group suggestion failed: {str(e)}")
