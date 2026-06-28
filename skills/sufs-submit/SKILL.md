# Skill: sufs-submit

Prepare and track SUFS FTCPEP reimbursement submission packets for Xfinity internet expenses.

## When to Use

- User wants to submit internet expenses to SUFS
- User needs to know which months are pending submission
- User wants to build the formatted packet text for portal entry

## Children

| Child | SUFS ID |
|-------|---------|
| Matteo Campilii | 20654016 |
| Lorenzo Campilii | 20654018 |

## Full Workflow

### Step 1 — Check what's pending

```bash
cd ~/stepup-reimbursement-engine
python3 -c "
import json
data = json.load(open('xfinity_bill_index.json'))
for b in data['bills']:
    if b['skip']: continue
    m_done = b['submitted_matteo']
    l_done = b['submitted_lorenzo']
    if not (m_done and l_done):
        print(f\"{b['month']} {b['label']}: Matteo={'done' if m_done else 'PENDING'} | Lorenzo={'done' if l_done else 'PENDING'} | \${b['total_amount']:.2f}\")
"
```

### Step 2 — Download any missing PDFs

```bash
python3 download_xfinity_bills.py --all
```

### Step 3 — Prepare packets

```bash
# All pending months, both children
python3 prepare_sufs_packet.py --all --child both --pending-only

# Single month
python3 prepare_sufs_packet.py --month 2025-01 --child both
```

Packets land in: `~/Downloads/StepUp-Submissions-2025/<YYYY-MM>/<Child>-Xfinity-<YYYY-MM>/`

Each folder contains:
- `submission-form.txt` — copy-paste ready text for the SUFS portal
- `Xfinity-MonYYYY.pdf` — the bill PDF to attach

### Step 4 — Submit on the SUFS portal

1. Go to https://sufsportal.com
2. Log in with Italo's credentials
3. Navigate to Reimbursement → New Submission
4. Select student (Matteo or Lorenzo)
5. Category: Internet Service
6. Copy values from `submission-form.txt`
7. Attach the bill PDF
8. Submit

### Step 5 — Mark as submitted

```bash
# After portal submission, update the index
python3 prepare_sufs_packet.py --month 2025-01 --child matteo --mark-submitted
```

Or edit `xfinity_bill_index.json` directly and set `"submitted_matteo": true`.

## Expense Split Logic

Internet bills are split 50/50 between Matteo and Lorenzo.

If the total is an odd cent, Matteo gets the extra cent (e.g., $92.85 / $92.84).

The pre-calculated splits are in `xfinity_bill_index.json` under `split_matteo` and `split_lorenzo`.

## Key Numbers

- Total internet reimbursable (17 submittable months): ~$1,990.94
- Per child: ~$995.47
- Nov 2025: skipped (credit month)

## SUFS Portal

URL: https://sufsportal.com
Account: Italo Campilii (parent/guardian)

## File Locations

| What | Where |
|------|-------|
| Bill PDFs | `~/Downloads/Xfinity-2025-Bills/` |
| Submission packets | `~/Downloads/StepUp-Submissions-2025/<YYYY-MM>/` |
| Bill index | `~/stepup-reimbursement-engine/xfinity_bill_index.json` |
| Other expense packets | `~/Downloads/StepUp-PEP-Rebuild/ready-to-submit/` |
