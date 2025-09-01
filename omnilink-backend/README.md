# OmniLink Backend

FastAPI backend for OmniLink platform.

## Quickstart

```bash
cd /workspace/omnilink-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Auth

- Signup: `POST /api/signup` with body `{ email, password, role, display_name, website_url? }`
- Token: `POST /api/auth/token` with form `username` (email) and `password`
- Use `Authorization: Bearer <token>` for protected endpoints

## Business

- Create product: `POST /api/business/products`
- List my products: `GET /api/business/products`

## Affiliate

- Marketplace: `GET /api/affiliate/marketplace`
- Select product: `POST /api/affiliate/select/{product_id}`
- My selections: `GET /api/affiliate/selections`

## Tracking

- Tracking redirect: `GET /api/t/{product_id}?affiliate_id=<id>`

## Sales

- Record sale: `POST /api/sales` with query/body params `product_id`, `quantity?`, `unit_price?`, `currency?`, `affiliate_id?`, `external_order_id?`

## Dashboards

- Affiliate dashboard: `GET /api/dashboard/affiliate`
- Business product tracker: `GET /api/dashboard/business`
