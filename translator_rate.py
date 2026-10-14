#!/usr/bin/env python3
"""translator-rate-lite: per-word rate -> real hourly, rate-cut cost, job CSV check.

Standard library only. No network. Never writes or deletes files (read-only CSV input).

Commands:
  hourly  --rate 0.09 --wph 450 [--target 40]
  cut     --rate 0.10 --new-rate 0.09 --words-month 40000
  jobs    jobs.csv [--today YYYY-MM-DD] [--target 40]
"""
import argparse
import csv
import datetime as dt
import sys


def money(x):
    return f"{x:,.2f}"


def cmd_hourly(a):
    hourly = a.rate * a.wph
    print(f"Rate {a.rate:.4f}/word x {a.wph:g} words/hour = {money(hourly)} per hour")
    if a.target:
        need = a.target / a.wph
        print(f"For {money(a.target)}/hour at {a.wph:g} words/hour you need {need:.4f}/word")
        print("Target reached." if hourly >= a.target else
              f"Gap to target: {money(a.target - hourly)} per hour")
    print("Note: words/hour should include research, queries, QA and admin time.")
    return 0


def cmd_cut(a):
    diff = a.rate - a.new_rate
    month = diff * a.words_month
    pct = diff / a.rate * 100 if a.rate else 0
    print(f"Cut: {a.rate:.4f} -> {a.new_rate:.4f} per word ({pct:.1f}%)")
    print(f"Per month ({a.words_month:g} words): {money(month)}")
    print(f"Per year: {money(month * 12)}")
    if a.wph:
        print(f"Real hourly drops from {money(a.rate * a.wph)} to {money(a.new_rate * a.wph)}")
    if a.new_rate > 0 and diff > 0:
        print(f"To earn the same you would need {a.rate / a.new_rate * 100 - 100:.1f}% more words.")
    return 0


def parse_date(s):
    s = (s or "").strip()
    return dt.date.fromisoformat(s) if s else None


def cmd_jobs(a):
    today = parse_date(a.today) or dt.date.today()
    try:
        f = open(a.csv, newline="", encoding="utf-8-sig")
    except OSError as e:
        print(f"Cannot read {a.csv}: {e}", file=sys.stderr)
        return 1
    tot_fee = tot_hours = outstanding = 0.0
    with f:
        rows = list(csv.DictReader(f))
    need = {"client", "job", "words", "rate_per_word", "hours", "invoice_date", "terms_days", "paid_date"}
    if not rows or not need <= set(rows[0].keys()):
        print("CSV needs columns: " + ", ".join(sorted(need)), file=sys.stderr)
        return 1
    print(f"{'Job':<24}{'Client':<16}{'Fee':>10}{'Real/h':>9}  Status")
    by_client = {}
    for i, r in enumerate(rows, start=2):
        try:
            fee = float(r["words"]) * float(r["rate_per_word"])
            hours = float(r["hours"])
            inv = parse_date(r["invoice_date"])
            terms = int(r["terms_days"] or 30)
            paid = parse_date(r["paid_date"])
        except ValueError as e:
            print(f"Line {i}: skipped ({e})", file=sys.stderr)
            continue
        hr = fee / hours if hours > 0 else 0.0
        if paid:
            status = "paid"
            by_client.setdefault(r["client"], []).append((paid - inv).days if inv else 0)
        elif not inv:
            status = "not invoiced"
        else:
            due = inv + dt.timedelta(days=terms)
            outstanding += fee
            status = "open" if due >= today else f"OVERDUE {(today - due).days}d"
        tot_fee += fee
        tot_hours += hours
        flag = " <below target" if a.target and hr < a.target else ""
        print(f"{r['job'][:23]:<24}{r['client'][:15]:<16}{money(fee):>10}{money(hr):>9}  {status}{flag}")
    print("-" * 70)
    if tot_hours:
        print(f"Total fees {money(tot_fee)} | hours {tot_hours:g} | real hourly {money(tot_fee / tot_hours)}")
    print(f"Still to collect: {money(outstanding)}")
    for c, d in sorted(by_client.items()):
        print(f"  {c}: pays in {sum(d) / len(d):.0f} days on average ({len(d)} paid)")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    h = s.add_parser("hourly")
    h.add_argument("--rate", type=float, required=True, help="per-word rate")
    h.add_argument("--wph", type=float, required=True, help="words per hour, all-in")
    h.add_argument("--target", type=float, help="target hourly")
    h.set_defaults(fn=cmd_hourly)
    c = s.add_parser("cut")
    c.add_argument("--rate", type=float, required=True)
    c.add_argument("--new-rate", type=float, required=True)
    c.add_argument("--words-month", type=float, required=True)
    c.add_argument("--wph", type=float, help="optional words per hour")
    c.set_defaults(fn=cmd_cut)
    j = s.add_parser("jobs")
    j.add_argument("csv")
    j.add_argument("--today", help="YYYY-MM-DD (default: today)")
    j.add_argument("--target", type=float)
    j.set_defaults(fn=cmd_jobs)
    a = p.parse_args()
    try:
        return a.fn(a)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
