"""Invoice Ninja API v5 integration service"""
import aiohttp
import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class InvoiceNinjaService:
    """Service for integrating with Invoice Ninja API v5"""
    
    def __init__(self):
        self.enabled = settings.INVOICE_NINJA_ENABLED
        self.base_url = settings.INVOICE_NINJA_URL.rstrip('/') if settings.INVOICE_NINJA_URL else None
        self.api_token = settings.INVOICE_NINJA_API_TOKEN
        self.api_version = settings.INVOICE_NINJA_API_VERSION
        
        if self.enabled and not (self.base_url and self.api_token):
            logger.warning("Invoice Ninja is enabled but credentials are not configured")
            self.enabled = False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "X-Api-Token": self.api_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make an API request to Invoice Ninja"""
        if not self.enabled:
            logger.debug("Invoice Ninja is disabled")
            return None
        
        url = f"{self.base_url}/api/{self.api_version}/{endpoint.lstrip('/')}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=self._get_headers(),
                    json=data,
                    params=params
                ) as response:
                    if response.status in (200, 201):
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Invoice Ninja API error: {response.status} - {error_text}"
                        )
                        return None
        except Exception as e:
            logger.error(f"Error making Invoice Ninja API request: {str(e)}")
            return None
    
    async def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get client details by ID
        
        Args:
            client_id: Invoice Ninja client ID
            
        Returns:
            Client data or None
        """
        return await self._request("GET", f"clients/{client_id}")
    
    async def get_clients(
        self,
        per_page: int = 100,
        page: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get all clients
        
        Args:
            per_page: Results per page
            page: Page number
            
        Returns:
            List of clients or None
        """
        response = await self._request(
            "GET",
            "clients",
            params={"per_page": per_page, "page": page}
        )
        if response and "data" in response:
            return response["data"]
        return None
    
    async def create_client(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        address1: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new client in Invoice Ninja
        
        Args:
            name: Client name
            email: Client email
            phone: Client phone
            website: Client website
            address1: Street address
            city: City
            state: State/Province
            postal_code: ZIP/Postal code
            country_id: Country ID (numeric)
            **kwargs: Additional client fields
            
        Returns:
            Created client data or None
        """
        client_data = {
            "name": name,
        }
        
        if email:
            client_data["contacts"] = [{"email": email}]
        if phone:
            client_data["phone"] = phone
        if website:
            client_data["website"] = website
        if address1:
            client_data["address1"] = address1
        if city:
            client_data["city"] = city
        if state:
            client_data["state"] = state
        if postal_code:
            client_data["postal_code"] = postal_code
        if country_id:
            client_data["country_id"] = country_id
        
        # Add any additional fields
        client_data.update(kwargs)
        
        response = await self._request("POST", "clients", data=client_data)
        if response and "data" in response:
            return response["data"]
        return None
    
    async def update_client(
        self,
        client_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Update a client
        
        Args:
            client_id: Invoice Ninja client ID
            **kwargs: Fields to update
            
        Returns:
            Updated client data or None
        """
        response = await self._request("PUT", f"clients/{client_id}", data=kwargs)
        if response and "data" in response:
            return response["data"]
        return None
    
    async def search_client_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Search for a client by email
        
        Args:
            email: Client email
            
        Returns:
            Client data or None
        """
        response = await self._request(
            "GET",
            "clients",
            params={"email": email}
        )
        if response and "data" in response and len(response["data"]) > 0:
            return response["data"][0]
        return None
    
    async def get_invoices_for_client(
        self,
        client_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get all invoices for a client
        
        Args:
            client_id: Invoice Ninja client ID
            
        Returns:
            List of invoices or None
        """
        response = await self._request(
            "GET",
            "invoices",
            params={"client_id": client_id}
        )
        if response and "data" in response:
            return response["data"]
        return None
    
    async def get_client_balance(self, client_id: str) -> Optional[float]:
        """
        Get client's current balance
        
        Args:
            client_id: Invoice Ninja client ID
            
        Returns:
            Balance amount or None
        """
        client = await self.get_client(client_id)
        if client and "data" in client:
            return float(client["data"].get("balance", 0))
        return None
    
    async def sync_client_from_invoice_ninja(
        self,
        invoice_ninja_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch and return client data from Invoice Ninja for syncing
        
        Args:
            invoice_ninja_id: Invoice Ninja client ID
            
        Returns:
            Normalized client data or None
        """
        response = await self.get_client(invoice_ninja_id)
        if not response or "data" not in response:
            return None
        
        client_data = response["data"]
        
        # Normalize data for our database
        normalized = {
            "invoice_ninja_id": client_data.get("id"),
            "name": client_data.get("name"),
            "company": client_data.get("name"),
            "phone": client_data.get("phone"),
            "address": client_data.get("address1"),
            "city": client_data.get("city"),
            "state": client_data.get("state"),
            "zip_code": client_data.get("postal_code"),
            "invoice_ninja_data": client_data,
        }
        
        # Extract email from contacts
        if "contacts" in client_data and len(client_data["contacts"]) > 0:
            normalized["email"] = client_data["contacts"][0].get("email")
        
        return normalized
    
    async def test_connection(self) -> bool:
        """Test connection to Invoice Ninja API"""
        if not self.enabled:
            return False
        
        response = await self._request("GET", "clients", params={"per_page": 1})
        return response is not None


# Global instance
invoice_ninja_service = InvoiceNinjaService()
