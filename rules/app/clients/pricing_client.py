"""Pricing service client for optional price resolution."""

import httpx
from typing import Dict, Any, List, Optional
from app.config import settings


class PricingClient:
    """Client for the Pricing service."""
    
    def __init__(self):
        self.base_url = settings.pricing_base_url
        self.client = httpx.AsyncClient(timeout=10.0) if self.base_url else None
    
    async def resolve_ref(self, ref: str) -> Optional[Dict[str, Any]]:
        """Resolve a single pricing reference."""
        if not self.base_url or not self.client:
            return None
        
        try:
            response = await self.client.get(f"{self.base_url}/v1/resolve", params={"ref": ref})
            response.raise_for_status()
            data = response.json()
            
            # Convert cents to dollars if the pricing service returns cents
            if "amount_cents" in data:
                data["amount_dollars"] = data["amount_cents"] / 100.0
                del data["amount_cents"]
            
            return data
        except (httpx.RequestError, httpx.HTTPStatusError):
            return None
    
    async def resolve_refs_batch(self, refs: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Resolve multiple pricing references in batch."""
        if not self.base_url or not self.client:
            return {ref: None for ref in refs}
        
        try:
            response = await self.client.post(f"{self.base_url}/v1/resolve-batch", json={"refs": refs})
            response.raise_for_status()
            data = response.json()
            prices = data.get("prices", {ref: None for ref in refs})
            
            # Convert cents to dollars for all resolved prices
            for ref, price_data in prices.items():
                if price_data and "amount_cents" in price_data:
                    price_data["amount_dollars"] = price_data["amount_cents"] / 100.0
                    del price_data["amount_cents"]
            
            return prices
        except (httpx.RequestError, httpx.HTTPStatusError):
            return {ref: None for ref in refs}
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()


# Global pricing client instance
pricing_client = PricingClient()
