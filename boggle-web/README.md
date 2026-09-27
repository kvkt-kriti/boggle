# Boggle web

Next.js frontend for **Boggle** (AP Credit Advisor). Talks to the thin Python API in `../boggle_api/`, which wraps the existing `ap_transfer` advisor — no recommend/compare logic is duplicated in JavaScript.

## Setup

```bash
cp .env.example .env.local
# edit NEXT_PUBLIC_API_URL if needed
npm install
```

## Run (with API)

From the **repo root**:

```bash
# terminal 1 — API (loads data/ap_equivalencies.json via ap_transfer)
pip install -r boggle_api/requirements.txt -r requirements.txt
python -m uvicorn boggle_api.main:app --reload --port 8000

# terminal 2 — web
cd boggle-web
npm run dev
```

Open http://localhost:3000

## Production build

```bash
npm run build
npm start
```

## Deploy notes

- **Frontend (Vercel):** set `NEXT_PUBLIC_API_URL` to your public API origin (HTTPS, no trailing slash).
- **API:** run `uvicorn boggle_api.main:app` on any Python host; set `BOGGLE_CORS_ORIGINS` to your Vercel domain(s), comma-separated.
- Do not hardcode localhost in client code; only `.env.local` / host env vars.
