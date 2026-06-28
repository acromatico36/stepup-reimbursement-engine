# SUFS FTCPEP Reimbursement — Build Loop

## Opportunity Sizing

### Children
- Matteo Campilii — SUFS ID 20654016
- Lorenzo Campilii — SUFS ID 20654018

### Bill History (Xfinity Internet)

| Month | Total Bill | Per Child (50%) | Matteo Submitted | Lorenzo Submitted |
|-------|-----------|-----------------|-----------------|-------------------|
| Jan 2025 | $120.46 | $60.23 | No | No |
| Feb 2025 | $185.69 | $92.85 / $92.84 | No | No |
| Mar 2025 | $55.23 | $27.62 / $27.61 | No | No |
| Apr 2025 | $120.46 | $60.23 | No | No |
| May 2025 | $148.78 | $74.39 | No | No |
| Jun 2025 | $175.15 | $87.58 / $87.57 | No | No |
| Jul 2025 | $181.94 | $90.97 | No | No |
| Aug 2025 | $164.00 | $82.00 | No | No |
| Sep 2025 | $164.00 | $82.00 | No | No |
| Oct 2025 | $164.00 | $82.00 | No | No |
| Nov 2025 | -$28.07 | SKIP (credit) | — | — |
| Dec 2025 | $161.98 | $80.99 | No | No |
| Jan 2026 | $51.05 | $25.53 / $25.52 | No | No |
| Feb 2026 | $51.05 | $25.53 / $25.52 | No | No |
| Mar 2026 | $51.05 | $25.53 / $25.52 | No | No |
| Apr 2026 | $51.05 | $25.53 / $25.52 | No | No |
| May 2026 | $51.05 | $25.53 / $25.52 | No | No |
| Jun 2026 | $51.05 | $25.53 / $25.52 | No | No |

### Totals

**Submittable bills (17 months, excluding Nov 2025 credit):**

Internet bills subtotal (gross): $1,990.94

Per-child subtotal: ~$995.47 each

**Total reimbursable across both children (internet only): ~$1,990.94**

> Note: This is internet expense only. Other SUFS-eligible expenses (soccer, gymnastics, CIE Learning, etc.) are tracked separately in `~/Downloads/StepUp-PEP-Rebuild/ready-to-submit/`.

### Other Submitted / Pending Expenses

Tracked in `~/Downloads/StepUp-PEP-Rebuild/ready-to-submit/`:
- 00_INDEX.md — master list
- Englewood Youth Soccer (Jan 2025)
- CIE Learning (Feb, Mar, Apr 2025)
- North Port Gymnastics (May, Jun 2025)
- Venice Area Youth Soccer (Jun 2025)

## Submission Workflow

1. Run `python3 download_xfinity_bills.py --all` — pull any missing PDFs
2. Run `python3 prepare_sufs_packet.py --all --child both --pending-only` — build packets for all unsubmitted months
3. Open the SUFS portal: https://sufsportal.com
4. Submit each packet manually (copy text from `submission-form.txt`, attach PDF)
5. After submitting, run with `--mark-submitted` to update `xfinity_bill_index.json`

## Next Actions

- [ ] Verify SUFS portal accepts "Internet Service" as a reimbursable expense category for FTCPEP
- [ ] Submit Jan 2025 as a test case to confirm packet format is accepted
- [ ] Batch submit remaining months after first approval
- [ ] Set up monthly reminder to download new bill and submit within 30 days of statement date
- [ ] Evaluate other household educational expenses for SUFS eligibility

## SUFS FTCPEP Program Notes

- Program: Florida Tax Credit Scholarship — Educational Progress (FTCPEP)
- Administrator: Step Up For Students
- Eligibility: Home education families meeting income requirements
- Reimbursable categories include: curriculum, tutoring, educational technology, internet service (for home education)
- Submission deadline: Expenses must be submitted within the program year window
- Documentation required: Itemized receipt or statement showing provider, amount, and date
