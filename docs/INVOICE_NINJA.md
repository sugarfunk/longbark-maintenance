# Invoice Ninja Integration Guide

LongBark integrates with Invoice Ninja v5 to link client sites with billing records, creating a unified client management experience.

## Benefits

- **Link sites to Invoice Ninja clients** for unified client records
- **Display billing status** on site detail pages
- **Quick access to client billing** from the dashboard
- **Automatic client synchronization** from Invoice Ninja
- **Client portal integration** showing both sites and billing

## Prerequisites

- Invoice Ninja v5 instance (self-hosted or cloud)
- API access enabled
- API token with appropriate permissions

## Getting an API Token

### Self-Hosted Invoice Ninja

1. Log in to your Invoice Ninja admin panel
2. Go to **Settings** → **Account Management** → **API Tokens**
3. Click **Create Token**
4. Give it a name: "LongBark Integration"
5. Select permissions: `clients:read`, `clients:write`, `invoices:read`
6. Click **Save**
7. Copy the token (you won't see it again!)

### Invoice Ninja Cloud

1. Log in to your Invoice Ninja account
2. Navigate to **Settings** → **Account Management**
3. Under **API Tokens**, click **Create New Token**
4. Name: "LongBark Integration"
5. Copy the generated token

## Configuration

### Basic Setup

Edit your `.env` file:

```bash
# Enable Invoice Ninja integration
INVOICE_NINJA_ENABLED=True

# Your Invoice Ninja URL (no trailing slash)
INVOICE_NINJA_URL=https://invoice.yourdomain.com

# API Token from Invoice Ninja
INVOICE_NINJA_API_TOKEN=your-api-token-here

# API Version (default: v5)
INVOICE_NINJA_API_VERSION=v5
```

### Restart Services

After configuration:

```bash
docker-compose restart backend celery_worker
```

### Test Connection

Test the Invoice Ninja connection:

```bash
docker-compose exec backend python -c "
from app.services.invoice_ninja_service import invoice_ninja_service
import asyncio
result = asyncio.run(invoice_ninja_service.test_connection())
print('Connection successful!' if result else 'Connection failed!')
"
```

## Linking Clients to Invoice Ninja

### Method 1: Manual Linking

1. Go to **Clients** page in LongBark
2. Click on a client or create a new one
3. In the client form, enter the **Invoice Ninja Client ID**
4. Save the client

### Method 2: Automatic Sync

Sync an existing Invoice Ninja client:

1. Go to **Clients** page
2. Click **Sync from Invoice Ninja**
3. Enter the Invoice Ninja Client ID
4. Click **Sync**

This will:
- Import client data from Invoice Ninja
- Create a new client in LongBark if it doesn't exist
- Link the records together

### Method 3: Bulk Import

Import all Invoice Ninja clients:

```bash
docker-compose exec backend python -c "
from app.services.invoice_ninja_service import invoice_ninja_service
from app.core.database import SessionLocal
from app.models import Client
import asyncio

async def import_clients():
    db = SessionLocal()
    clients = await invoice_ninja_service.get_clients(per_page=100)
    
    if clients:
        for in_client in clients:
            # Check if client already exists
            existing = db.query(Client).filter(
                Client.invoice_ninja_id == in_client['id']
            ).first()
            
            if not existing:
                # Create new client
                client = Client(
                    name=in_client['name'],
                    invoice_ninja_id=in_client['id'],
                    invoice_ninja_data=in_client,
                )
                db.add(client)
        
        db.commit()
        print(f'Imported {len(clients)} clients')
    db.close()

asyncio.run(import_clients())
"
```

## Linking Sites to Clients

Once clients are linked to Invoice Ninja:

1. Go to **Sites** page
2. Edit a site
3. Select the **Client** from the dropdown
4. Save

The site will now be associated with both the LongBark client and their Invoice Ninja record.

## Features

### Client Dashboard Integration

On the client detail page, you'll see:

- **Client Information** from Invoice Ninja
- **All sites** managed for this client
- **Billing Summary**: Balance, outstanding invoices
- **Quick Links** to Invoice Ninja client page

### Site Detail Page

On site detail pages (for sites with clients):

- **Client Name** with link to client page
- **Billing Status** badge (paid, overdue, etc.)
- **Quick link** to Invoice Ninja

### Client Portal

Clients can log in to see:

- **Their sites** and monitoring status
- **Direct link** to Invoice Ninja for billing
- **Reports** for their sites

## API Endpoints

LongBark provides API endpoints for Invoice Ninja integration:

### Sync Client from Invoice Ninja

```http
POST /api/v1/clients/{client_id}/sync-invoice-ninja
Content-Type: application/json
Authorization: Bearer <your-token>
```

### Get Client with Invoice Data

```http
GET /api/v1/clients/{client_id}
Authorization: Bearer <your-token>
```

Response includes `invoice_ninja_data` field with full Invoice Ninja client record.

## Automatic Client Creation

When adding a new site, you can automatically create a client in Invoice Ninja:

1. Enable in settings (coming soon)
2. Add site with client email
3. LongBark creates client in Invoice Ninja
4. Links records automatically

## Data Synchronization

### What Data is Synced?

From Invoice Ninja to LongBark:
- Client name
- Email address
- Phone number
- Company name
- Address (street, city, state, zip, country)
- Current balance
- Invoice status

### Sync Frequency

- **Manual**: Click "Sync" button on client page
- **Automatic**: Syncs when viewing client details (cached for 1 hour)
- **API**: Use API endpoints for real-time sync

### Sync Direction

Current implementation: Invoice Ninja → LongBark (one-way)

LongBark pulls data from Invoice Ninja but doesn't push back. This ensures Invoice Ninja remains the source of truth for billing data.

## Use Cases

### 1. Hosting Business Dashboard

Perfect for web hosting businesses:

- Monitor all client sites in one dashboard
- See which clients have outstanding invoices
- Link site issues to billing status
- Provide clients with unified view of hosting + billing

### 2. Agency Client Management

For agencies managing multiple client sites:

- Track all sites per client
- Link deliverables to billing
- Generate reports combining hosting + billing data
- Client portal for transparency

### 3. Managed WordPress Hosting

For WordPress hosting providers:

- Monitor WordPress updates across all clients
- Link maintenance tasks to billing
- Bill per site or per client
- Automated reports for clients

## Troubleshooting

### "Connection failed" Error

1. **Check URL format**:
   - Must include `https://`
   - No trailing slash
   - Example: `https://invoice.yourdomain.com`

2. **Verify API token**:
   - Token is valid and not expired
   - Token has correct permissions
   - No extra spaces in token

3. **Test with curl**:
   ```bash
   curl -H "X-Api-Token: your-token" \
        -H "Accept: application/json" \
        https://invoice.yourdomain.com/api/v5/clients?per_page=1
   ```

### Client Data Not Syncing

1. **Check Invoice Ninja API version**:
   - LongBark supports v5
   - Verify your Invoice Ninja version

2. **Check client exists in Invoice Ninja**:
   - Log in to Invoice Ninja
   - Search for the client
   - Note the client ID (from URL or API)

3. **Check permissions**:
   - API token must have `clients:read` permission
   - For creating clients: `clients:write` permission

### "Client not found" Error

1. **Verify Client ID format**:
   - Invoice Ninja uses alphanumeric IDs
   - Example: `VolejRejNm` or `1`

2. **Check in Invoice Ninja directly**:
   ```bash
   curl -H "X-Api-Token: your-token" \
        https://invoice.yourdomain.com/api/v5/clients/CLIENT_ID
   ```

## Security Considerations

### API Token Security

- **Never commit** API tokens to version control
- **Use environment variables** only
- **Restrict token permissions** to minimum required
- **Rotate tokens** periodically
- **Use separate tokens** for development and production

### Data Privacy

- Invoice Ninja data is stored in LongBark database
- Consider data residency requirements
- Use encrypted connections (HTTPS) only
- Implement access controls for client data

### Network Security

If running on separate servers:

- Use VPN or Tailscale for secure communication
- Don't expose Invoice Ninja API to public internet
- Use firewall rules to restrict access
- Consider using API proxy

## Advanced Configuration

### Custom Client Mapping

Customize how Invoice Ninja data maps to LongBark clients:

Edit `backend/app/services/invoice_ninja_service.py`:

```python
# Customize field mapping
normalized = {
    "invoice_ninja_id": client_data.get("id"),
    "name": client_data.get("name"),
    "company": client_data.get("name"),
    # Add custom fields here
    "custom_field": client_data.get("custom_value1"),
}
```

### Webhook Integration (Future)

Invoice Ninja supports webhooks for real-time updates:

1. Configure webhook in Invoice Ninja settings
2. Point to LongBark webhook endpoint
3. Automatically sync on client changes

## Resources

- Invoice Ninja Documentation: https://invoiceninja.github.io/
- Invoice Ninja API v5 Docs: https://api-docs.invoicing.co/
- Invoice Ninja GitHub: https://github.com/invoiceninja/invoiceninja
- Self-Hosting Guide: https://invoiceninja.github.io/selfhost.html

## API Reference

### Invoice Ninja Service Methods

```python
from app.services import invoice_ninja_service

# Get client by ID
client = await invoice_ninja_service.get_client(client_id)

# Get all clients
clients = await invoice_ninja_service.get_clients(per_page=100)

# Create new client
client = await invoice_ninja_service.create_client(
    name="Client Name",
    email="client@example.com",
    phone="555-1234",
    website="https://clientsite.com"
)

# Update client
updated = await invoice_ninja_service.update_client(
    client_id="abc123",
    phone="555-5678"
)

# Search by email
client = await invoice_ninja_service.search_client_by_email(
    "client@example.com"
)

# Get invoices for client
invoices = await invoice_ninja_service.get_invoices_for_client(client_id)

# Get client balance
balance = await invoice_ninja_service.get_client_balance(client_id)
```

## Roadmap

Future enhancements planned:

- ✅ View client billing status
- ✅ Link sites to clients
- ✅ Sync client data from Invoice Ninja
- 🔄 Auto-create clients in Invoice Ninja
- 🔄 Two-way sync
- 🔄 Webhook support for real-time updates
- 🔄 Generate invoices from LongBark
- 🔄 Link monitoring reports to invoices
- 🔄 Client portal with integrated billing

Legend: ✅ Complete | 🔄 Planned
