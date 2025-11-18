"""SSL certificate monitoring service for checking certificate validity and expiry"""
import ssl
import socket
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
from app.core.config import settings

logger = logging.getLogger(__name__)


class SSLMonitor:
    """Service for monitoring SSL certificate validity and expiration"""

    def __init__(self):
        self.warning_days = settings.SSL_WARNING_DAYS

    def _get_hostname_from_url(self, url: str) -> str:
        """Extract hostname from URL"""
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path
        # Remove port if present
        if ':' in hostname:
            hostname = hostname.split(':')[0]
        return hostname

    def _parse_certificate(self, cert_der: bytes) -> x509.Certificate:
        """Parse DER-encoded certificate"""
        return x509.load_der_x509_certificate(cert_der, default_backend())

    def _get_certificate_subject(self, cert: x509.Certificate) -> str:
        """Extract subject from certificate"""
        try:
            return cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except (IndexError, AttributeError):
            return "Unknown"

    def _get_certificate_issuer(self, cert: x509.Certificate) -> str:
        """Extract issuer from certificate"""
        try:
            return cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except (IndexError, AttributeError):
            return "Unknown"

    def _get_certificate_chain_info(self, cert_chain: List[bytes]) -> List[Dict[str, str]]:
        """Extract information from certificate chain"""
        chain_info = []
        for cert_der in cert_chain:
            try:
                cert = self._parse_certificate(cert_der)
                chain_info.append({
                    "subject": self._get_certificate_subject(cert),
                    "issuer": self._get_certificate_issuer(cert),
                    "valid_from": cert.not_valid_before_utc.isoformat(),
                    "valid_until": cert.not_valid_after_utc.isoformat(),
                })
            except Exception as e:
                logger.warning(f"Failed to parse certificate in chain: {str(e)}")
                chain_info.append({
                    "error": f"Failed to parse: {str(e)}"
                })
        return chain_info

    async def check_ssl_certificate(self, url: str) -> Dict[str, Any]:
        """
        Check SSL certificate for a given URL

        Args:
            url: The URL to check (e.g., https://example.com)

        Returns:
            Dict containing:
                - is_valid: Boolean indicating if certificate is valid
                - issuer: Certificate issuer
                - subject: Certificate subject
                - valid_from: Certificate valid from date
                - valid_until: Certificate expiry date
                - days_until_expiry: Days until certificate expires
                - error_message: Error message if check failed
                - certificate_chain: List of certificates in chain
        """
        result = {
            "is_valid": False,
            "issuer": None,
            "subject": None,
            "valid_from": None,
            "valid_until": None,
            "days_until_expiry": None,
            "error_message": None,
            "certificate_chain": None
        }

        try:
            # Extract hostname from URL
            hostname = self._get_hostname_from_url(url)
            port = 443

            # Create SSL context
            context = ssl.create_default_context()

            # Get certificate
            with socket.create_connection((hostname, port), timeout=30) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate in DER format
                    cert_der = ssock.getpeercert(binary_form=True)

                    # Get certificate chain if available
                    cert_chain = []
                    try:
                        # Try to get full chain (not always available)
                        cert_chain = [cert_der]
                    except Exception:
                        cert_chain = [cert_der]

                    # Parse the main certificate
                    cert = self._parse_certificate(cert_der)

                    # Extract certificate information
                    subject = self._get_certificate_subject(cert)
                    issuer = self._get_certificate_issuer(cert)

                    # Get validity dates
                    valid_from = cert.not_valid_before_utc
                    valid_until = cert.not_valid_after_utc

                    # Calculate days until expiry
                    now = datetime.now(timezone.utc)
                    days_until_expiry = (valid_until - now).days

                    # Check if certificate is valid
                    is_valid = valid_from <= now <= valid_until

                    # Get certificate chain info
                    chain_info = self._get_certificate_chain_info(cert_chain)

                    # Store results
                    result["is_valid"] = is_valid
                    result["issuer"] = issuer
                    result["subject"] = subject
                    result["valid_from"] = valid_from
                    result["valid_until"] = valid_until
                    result["days_until_expiry"] = days_until_expiry
                    result["certificate_chain"] = chain_info

                    if not is_valid:
                        if now < valid_from:
                            result["error_message"] = "Certificate not yet valid"
                        else:
                            result["error_message"] = "Certificate expired"
                    elif days_until_expiry <= self.warning_days:
                        result["error_message"] = f"Certificate expires in {days_until_expiry} days"

                    logger.info(
                        f"SSL check for {hostname}: "
                        f"valid={is_valid}, issuer={issuer}, "
                        f"days_until_expiry={days_until_expiry}"
                    )

        except ssl.SSLError as e:
            result["error_message"] = f"SSL error: {str(e)}"
            logger.error(f"SSL error checking {url}: {str(e)}")

        except socket.gaierror as e:
            result["error_message"] = f"DNS resolution failed: {str(e)}"
            logger.error(f"DNS error checking {url}: {str(e)}")

        except socket.timeout:
            result["error_message"] = "Connection timeout"
            logger.error(f"Timeout checking SSL for {url}")

        except ConnectionRefusedError:
            result["error_message"] = "Connection refused"
            logger.error(f"Connection refused for {url}")

        except Exception as e:
            result["error_message"] = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error checking SSL for {url}: {str(e)}")

        return result

    async def check_multiple_certificates(self, urls: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Check SSL certificates for multiple URLs concurrently

        Args:
            urls: List of URLs to check

        Returns:
            Dict mapping URL to check results
        """
        import asyncio

        tasks = [self.check_ssl_certificate(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results to URLs
        url_results = {}
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                url_results[url] = {
                    "is_valid": False,
                    "issuer": None,
                    "subject": None,
                    "valid_from": None,
                    "valid_until": None,
                    "days_until_expiry": None,
                    "error_message": f"Check failed: {str(result)}",
                    "certificate_chain": None
                }
            else:
                url_results[url] = result

        return url_results


# Global instance
ssl_monitor = SSLMonitor()
