# Step Up For Students — FTCPEP Reimbursement Engine

Automation tools for managing Florida Tax Credit Scholarship Program for Educational Progress (FTCPEP) reimbursement submissions through the Step Up For Students (SUFS) portal.

## Kids

| Child | SUFS ID |
|-------|---------|
| Matteo Campilii | 20654016 |
| Lorenzo Campilii | 20654018 |

## What This System Does

1. **Downloads Xfinity internet bills** — using the authenticated Xfinity API (Bearer JWT from Safari localStorage) to pull monthly PDF statements
2. **Prepares submission packets** — formats bill PDFs with the required SUFS submission form text, splits internet costs 50/50 between Matteo and Lorenzo
3. **Tracks submission status** — `xfinity_bill_index.json` records every bill, split amount, and whether each child's claim has been submitted

## SUFS Portal

Portal URL: [https://sufsportal.com](https://sufsportal.com)

Reimbursement is submitted manually through the portal. These scripts prepare the packets and track what has/has not been submitted.

## Xfinity Bill API

The Xfinity bill PDF API requires a Bearer JWT token obtained from Safari's localStorage.

**Endpoint:**
```
GET https://api.sc.xfinity.com/session/ssm/bill/pdf?statementDate=MM-DD-YYYY&signed=true
Authorization: Bearer <JWT>
```

**Token location:** Safari localStorage key:
```
dss-myaccount-production_https://api.sc.xfinity.com/session
```

The token is nested inside the stored JSON object. `download_xfinity_bills.py` retrieves it automatically via AppleScript.

## Directory Layout

```
stepup-reimbursement-engine/
├── README.md
├── build_loop.md                    # Opportunity sizing, status tracker
├── xfinity_bill_index.json          # All 18 bills, amounts, submission status
├── download_xfinity_bills.py        # Download PDFs via Xfinity API
├── prepare_sufs_packet.py           # Build submission packets
└── skills/
    ├── xfinity-download/SKILL.md    # Claude Code skill: download bills
    └── sufs-submit/SKILL.md         # Claude Code skill: SUFS workflow
```

## Local Bill Storage

Downloaded bills land in `~/Downloads/Xfinity-2025-Bills/`

Formatted as: `Xfinity-MonYYYY.pdf` (e.g., `Xfinity-Jan2025.pdf`)

## Submission Packet Storage

Packets are organized under `~/Downloads/StepUp-Submissions-2025/<YYYY-MM>/`

Each month folder contains:
- `submission-form.txt` — filled-out SUFS submission text
- Receipt PDF (copy of the Xfinity bill)

## Quick Start

```bash
# Download all bills Jan2025–present
python3 download_xfinity_bills.py --all

# Download specific months
python3 download_xfinity_bills.py --months 2025-01 2025-02 2025-03

# Prepare a packet for Matteo, February 2025
python3 prepare_sufs_packet.py --month 2025-02 --child matteo

# Prepare packets for both kids, all pending months
python3 prepare_sufs_packet.py --all --pending-only
```

## Internet Expense Split

Internet is a shared household expense. Bills are split 50/50 between Matteo and Lorenzo for SUFS reimbursement purposes. The split amounts are pre-calculated in `xfinity_bill_index.json`.

## Notes

- Nov 2025 was a credit month (-$28.07) — skipped, not submitted
- Submissions are manual through the SUFS portal; these tools prepare and organize packets only
- Always verify the SUFS portal accepts internet service as an eligible expense category before submitting new months
