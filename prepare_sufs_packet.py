#!/usr/bin/env python3
"""
prepare_sufs_packet.py
Build SUFS FTCPEP submission packets for Xfinity internet bills.

Each packet is a folder containing:
  - submission-form.txt  (filled-out SUFS form text ready to copy-paste into the portal)
  - <original_bill>.pdf  (copy of the Xfinity bill PDF)

Internet bills are split 50/50 between Matteo and Lorenzo by default.

Usage:
    # Single month, one child
    python3 prepare_sufs_packet.py --month 2025-01 --child matteo

    # Single month, both children
    python3 prepare_sufs_packet.py --month 2025-01 --child both

    # All pending (not yet submitted) months, both children
    python3 prepare_sufs_packet.py --all --child both --pending-only

    # Override the split amount
    python3 prepare_sufs_packet.py --month 2025-02 --child matteo --amount 92.85
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KIDS = {
    "matteo": {"name": "Matteo Campilii", "sufs_id": "20654016"},
    "lorenzo": {"name": "Lorenzo Campilii", "sufs_id": "20654018"},
}

INDEX_PATH = Path(__file__).parent / "xfinity_bill_index.json"
BILLS_DIR = Path(os.path.expanduser("~/Downloads/Xfinity-2025-Bills"))
SUBMISSIONS_DIR = Path(os.path.expanduser("~/Downloads/StepUp-Submissions-2025"))

EXPENSE_CATEGORY = "Internet Service"
PROVIDER = "Xfinity (Comcast)"
SERVICE_ADDRESS = "102 Naomi Pl, Rotonda West, FL 33947"


# ---------------------------------------------------------------------------
# Submission form template
# ---------------------------------------------------------------------------

FORM_TEMPLATE = """\
STEP UP FOR STUDENTS — FTCPEP REIMBURSEMENT SUBMISSION
=======================================================
Date Prepared: {prepared_date}

STUDENT INFORMATION
-------------------
Student Name: {student_name}
SUFS Student ID: {sufs_id}

EXPENSE INFORMATION
-------------------
Expense Category: {category}
Vendor/Provider: {provider}
Service Period: {service_period}
Invoice/Statement Date: {statement_date}
Total Invoice Amount: ${total_amount:.2f}
Amount Claimed (split): ${claimed_amount:.2f}
Split Basis: 50% of household internet — shared educational use between Matteo and Lorenzo

SERVICE DETAILS
---------------
Service Type: High-Speed Internet (required for online coursework and educational programs)
Service Address: {service_address}
Account Holder: Italo Campilii (parent/guardian)

SUPPORTING DOCUMENTATION
-------------------------
Attached: Xfinity monthly statement PDF ({pdf_filename})

NOTES
-----
This claim represents 50% of the Xfinity internet bill for {label}.
Internet service is used for online educational programs including CIE Learning
and other SUFS-approved digital curriculum.

---
Prepared by SUFS Reimbursement Engine
"""


def load_index() -> dict:
    with open(INDEX_PATH) as f:
        return json.load(f)


def save_index(data: dict):
    with open(INDEX_PATH, "w") as f:
        json.dump(data, f, indent=2)


def find_bill(index: dict, month: str) -> dict | None:
    for bill in index["bills"]:
        if bill["month"] == month:
            return bill
    return None


def service_period(month: str) -> str:
    dt = datetime.strptime(month, "%Y-%m")
    return dt.strftime("%B %Y")


def statement_date_human(month: str) -> str:
    year, mo = month.split("-")
    return f"{mo}/01/{year}"


def prepare_packet(bill: dict, child_key: str, override_amount: float | None = None) -> Path:
    """Build and write a submission packet. Returns the packet directory path."""
    kid = KIDS[child_key]
    month = bill["month"]

    if override_amount is not None:
        claimed = override_amount
    else:
        claimed = bill[f"split_{child_key}"]

    # Destination folder
    packet_dir = SUBMISSIONS_DIR / month / f"{child_key.capitalize()}-Xfinity-{month}"
    packet_dir.mkdir(parents=True, exist_ok=True)

    # Copy PDF
    pdf_src = BILLS_DIR / bill["pdf_filename"]
    pdf_dest = packet_dir / bill["pdf_filename"]
    if pdf_src.exists():
        shutil.copy2(pdf_src, pdf_dest)
        pdf_note = bill["pdf_filename"]
    else:
        pdf_note = f"{bill['pdf_filename']} (NOT FOUND — download first)"

    # Write form
    form_text = FORM_TEMPLATE.format(
        prepared_date=datetime.now().strftime("%Y-%m-%d"),
        student_name=kid["name"],
        sufs_id=kid["sufs_id"],
        category=EXPENSE_CATEGORY,
        provider=PROVIDER,
        service_period=service_period(month),
        statement_date=statement_date_human(month),
        total_amount=bill["total_amount"],
        claimed_amount=claimed,
        service_address=SERVICE_ADDRESS,
        pdf_filename=pdf_note,
        label=service_period(month),
    )
    form_path = packet_dir / "submission-form.txt"
    form_path.write_text(form_text)

    print(f"  [packet] {packet_dir.relative_to(Path.home())} — ${claimed:.2f} for {kid['name']}")
    return packet_dir


def mark_submitted(index: dict, month: str, child_key: str):
    for bill in index["bills"]:
        if bill["month"] == month:
            bill[f"submitted_{child_key}"] = True
            break


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Prepare SUFS FTCPEP submission packets for Xfinity internet bills."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--month", metavar="YYYY-MM", help="Specific month to prepare")
    group.add_argument("--all", action="store_true", help="Prepare packets for all months")
    parser.add_argument(
        "--child", choices=["matteo", "lorenzo", "both"], default="both",
        help="Which child to prepare the packet for (default: both)"
    )
    parser.add_argument(
        "--pending-only", action="store_true",
        help="Skip months already marked as submitted in xfinity_bill_index.json"
    )
    parser.add_argument(
        "--amount", type=float,
        help="Override the claimed amount (default: 50%% split from index)"
    )
    parser.add_argument(
        "--mark-submitted", action="store_true",
        help="After preparing, mark the month(s) as submitted in the index"
    )
    args = parser.parse_args()

    index = load_index()

    # Determine children
    children = ["matteo", "lorenzo"] if args.child == "both" else [args.child]

    # Determine bills to process
    if args.month:
        bills = [find_bill(index, args.month)]
        if bills[0] is None:
            print(f"Month {args.month} not found in index.")
            sys.exit(1)
    else:
        bills = [b for b in index["bills"] if not b.get("skip")]

    # Filter pending
    if args.pending_only:
        filtered = []
        for bill in bills:
            needed = [c for c in children if not bill.get(f"submitted_{c}")]
            if needed:
                filtered.append(bill)
        bills = filtered

    if not bills:
        print("No bills to process.")
        return

    total_prepared = 0
    for bill in bills:
        if bill.get("skip"):
            print(f"  [skip] {bill['label']} — {bill.get('skip_reason', 'skipped')}")
            continue
        for child_key in children:
            if args.pending_only and bill.get(f"submitted_{child_key}"):
                continue
            prepare_packet(bill, child_key, args.amount)
            total_prepared += 1
            if args.mark_submitted:
                mark_submitted(index, bill["month"], child_key)

    if args.mark_submitted:
        save_index(index)
        print(f"\nIndex updated — marked {total_prepared} submission(s) as submitted.")

    print(f"\nPackets prepared: {total_prepared}")
    print(f"Location: {SUBMISSIONS_DIR}")


if __name__ == "__main__":
    main()
