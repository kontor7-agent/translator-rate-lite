# translator-rate-lite

**Find out what your per-word rate really pays per hour – and which invoices are late.**

A tiny command-line tool for freelance translators. One Python file, no dependencies, no network.

## What it does

- `hourly` – per-word rate × words per hour = real hourly (and the rate needed for a target hourly)
- `cut` – what a requested rate cut costs you per month and per year
- `jobs` – reads a CSV of jobs: fee, real hourly per job, overdue/open invoices, money still to collect, average days-to-pay per client

The tool only reads the CSV you point it at. It never writes, changes or deletes files.

## Quick start

```
python translator_rate.py hourly --rate 0.09 --wph 450 --target 40
python translator_rate.py cut --rate 0.10 --new-rate 0.085 --words-month 40000 --wph 450
python translator_rate.py jobs sample-jobs.csv --today 2026-10-14 --target 40
```

CSV columns (see `sample-jobs.csv`): `client,job,words,rate_per_word,hours,invoice_date,terms_days,paid_date`. Dates are `YYYY-MM-DD`; leave `paid_date` empty while unpaid and `invoice_date` empty if not yet invoiced.

## Requirements

- Python 3.8+ (standard library only)

## Notes

- "Words per hour" should include research, queries, QA and admin time, otherwise the result is too rosy.
- The tool organises your numbers; it is not professional tax, accounting or legal help.

Created with AI assistance by an automated system.

## Full version

The lite tool is a command line calculator. The full kit is an Excel workbook (Excel 2010+, no macros) that adds:

- Jobs sheet with CAT word counts (new / fuzzy / repetitions), rush surcharge and minimum fee, calculated automatically
- Clients sheet with payment terms and an Overview dashboard (real hourly vs target, overdue invoices, table by client)
- Rate check sheet with a rate × speed grid
- A how-to sheet, one-page Quick-Start PDF and email templates (payment reminders, rate-cut replies, rush quotes)

Get it here: https://kontor7-agent.github.io/p/per-word-to-real-hourly-translator-rate-job-trac?s=github
