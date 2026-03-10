"""Chat service for AI-powered procurement assistant."""

import json
from typing import AsyncGenerator, List
from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.constants import COMMODITY_GROUPS, DEPARTMENTS
from app.database import get_database


class ChatService:
    """Service for the AI procurement assistant chat."""

    def __init__(self):
        self.client = None
        if OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    def is_available(self) -> bool:
        return self.client is not None

    async def _load_system_context(self) -> str:
        """Load current procurement data to give the AI full context."""
        db = get_database()
        context_parts = []

        # Stats
        stats = {"total_requests": 0, "total_value": 0, "by_status": {}}
        if db is not None:
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"archived": False},
                            {"archived": {"$exists": False}},
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1},
                        "total_value": {"$sum": "$total_cost"},
                    }
                },
            ]
            cursor = db["procurement_requests"].aggregate(pipeline)
            results = await cursor.to_list(length=None)
            stats = {
                "by_status": {
                    r["_id"]: {
                        "count": r["count"],
                        "total_value": round(r["total_value"], 2),
                    }
                    for r in results
                },
                "total_requests": sum(r["count"] for r in results),
                "total_value": round(sum(r["total_value"] for r in results), 2),
            }

        context_parts.append(f"### Current Statistics\n{json.dumps(stats, indent=2)}")

        # Recent requests (last 50)
        if db is not None:
            cursor = (
                db["procurement_requests"]
                .find(
                    {"$or": [{"archived": False}, {"archived": {"$exists": False}}]},
                    {
                        "title": 1,
                        "requestor_name": 1,
                        "vendor_name": 1,
                        "department": 1,
                        "status": 1,
                        "total_cost": 1,
                        "commodity_group_id": 1,
                        "created_at": 1,
                        "order_lines": 1,
                    },
                )
                .sort("created_at", -1)
                .limit(50)
            )
            requests = await cursor.to_list(length=None)

            if requests:
                req_summaries = []
                for r in requests:
                    cg = next(
                        (
                            g
                            for g in COMMODITY_GROUPS
                            if g["id"] == r.get("commodity_group_id")
                        ),
                        None,
                    )
                    order_lines_desc = ", ".join(
                        [
                            f"{ol.get('description', '?')} ({ol.get('amount', 0)} {ol.get('unit', 'units')} @ {ol.get('unit_price', 0)})"
                            for ol in r.get("order_lines", [])
                        ]
                    )
                    req_summaries.append(
                        {
                            "id": str(r["_id"]),
                            "title": r.get("title", ""),
                            "requestor": r.get("requestor_name", ""),
                            "vendor": r.get("vendor_name", ""),
                            "department": r.get("department", ""),
                            "status": r.get("status", ""),
                            "total_cost": r.get("total_cost", 0),
                            "commodity_group": cg["name"] if cg else "Unknown",
                            "category": cg["category"] if cg else "Unknown",
                            "items": order_lines_desc,
                            "created_at": (
                                r["created_at"].isoformat()
                                if r.get("created_at")
                                else ""
                            ),
                        }
                    )
                context_parts.append(
                    f"### Active Procurement Requests ({len(req_summaries)} shown)\n{json.dumps(req_summaries, indent=2)}"
                )
            else:
                context_parts.append(
                    "### Active Procurement Requests\nNo active requests in the system."
                )

        # Commodity groups
        cg_lines = [
            f"- {g['id']}: {g['category']} > {g['name']}" for g in COMMODITY_GROUPS
        ]
        context_parts.append(
            f"### Available Commodity Groups\n" + "\n".join(cg_lines)
        )

        # Departments
        context_parts.append(
            f"### Available Departments\n" + ", ".join(DEPARTMENTS)
        )

        return "\n\n".join(context_parts)

    def _build_system_prompt(self, context: str) -> str:
        return f"""You are **SANOVIO Procurement Assistant**, the AI-powered assistant for the SANOVIO Procurement Request Management System. You help users manage and understand their procurement data.

## Your Capabilities
- Answer questions about procurement requests, vendors, spending, departments, and system data
- Provide analytics, insights, and summaries about procurement activities
- Help users understand trends in their procurement data
- Guide users through creating new procurement requests (explain required fields)
- Suggest appropriate commodity groups for purchases
- Provide procurement best practices and advice
- Compare vendors, departments, and spending patterns

## Response Guidelines
- Be concise, helpful, and professional
- Use markdown formatting for clear structure (headers, bold, lists, tables)
- When showing multiple requests, use **markdown tables** with columns for key info
- Format monetary values with currency symbols (e.g., €1,234.56)
- When analyzing data, provide specific numbers and percentages
- If asked about something not in the data, clearly state that
- When helping create requests, explain all required fields: requestor name, title, vendor name, VAT ID, commodity group, department, order lines (description, unit price, amount, unit)
- Keep responses focused and actionable
- If the user greets you, respond warmly and briefly mention what you can help with

## Current System Data
{context}"""

    async def stream_chat(
        self, messages: List[dict]
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response based on conversation history."""
        if not self.client:
            yield json.dumps({"content": "AI service is not configured. Please set the OPENAI_API_KEY environment variable."})
            return

        context = await self._load_system_context()
        system_prompt = self._build_system_prompt(context)

        api_messages = [{"role": "system", "content": system_prompt}]

        for msg in messages[-20:]:
            api_messages.append(
                {"role": msg["role"], "content": msg["content"]}
            )

        try:
            stream = await self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=api_messages,
                temperature=0.3,
                stream=True,
                max_tokens=2000,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield json.dumps({"content": chunk.choices[0].delta.content})

        except Exception as e:
            yield json.dumps(
                {"content": f"\n\nSorry, I encountered an error: {str(e)}"}
            )
