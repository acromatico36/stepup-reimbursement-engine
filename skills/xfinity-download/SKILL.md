# Skill: xfinity-download

Download Xfinity internet bill PDFs using the authenticated Xfinity API and Safari's localStorage JWT.

## When to Use

- User asks to download Xfinity bills
- User needs to refresh the bill PDF library before building SUFS packets
- A bill PDF is missing from `~/Downloads/Xfinity-2025-Bills/`

## Prerequisites

1. Safari must be open and logged in to xfinity.com/myaccount
2. The localStorage key `dss-myaccount-production_https://api.sc.xfinity.com/session` must be present (it is set automatically when you load your account page)
3. Python 3.11+

## How to Run

```bash
cd ~/stepup-reimbursement-engine

# Download everything Jan 2025 through today
python3 download_xfinity_bills.py --all

# Download specific months
python3 download_xfinity_bills.py --months 2025-06 2025-07

# Provide a JWT manually (if AppleScript fails)
python3 download_xfinity_bills.py --all --token "eyJhbGci..."
```

## How the Token Works

The script uses AppleScript to run JavaScript inside Safari:
```javascript
localStorage.getItem('dss-myaccount-production_https://api.sc.xfinity.com/session')
```
The returned JSON object contains the `access_token` field used as the Bearer JWT.

## API Details

```
GET https://api.sc.xfinity.com/session/ssm/bill/pdf?statementDate=MM-DD-YYYY&signed=true
Authorization: Bearer <JWT>
```

`statementDate` uses the format `MM-DD-YYYY` with the first of the month (e.g., `01-01-2025` for January 2025).

## Output

Bills saved to: `~/Downloads/Xfinity-2025-Bills/`
Filename format: `Xfinity-MonYYYY.pdf` (e.g., `Xfinity-Jan2025.pdf`)

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `localStorage key not found` | Open Safari → go to xfinity.com/myaccount → sign in → retry |
| `HTTP 401` | JWT expired — reload xfinity.com/myaccount in Safari, then retry |
| `Response is not a PDF` | The API returned an error page; check that `statementDate` is a valid past statement date |
| AppleScript permission denied | System Preferences → Privacy & Security → Automation → allow Terminal to control Safari |
