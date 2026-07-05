---
title: How to Correct Your Personal Data
doc_type: guide
category: how-to
jurisdictions: [GLOBAL]
language: en
scenarios: [hr-hrsd-03, hr-hrsd-07]
tags: [data-correction, address, records, how-to]
---
# How to Correct Your Personal Data

## What you can correct

Address, legal and preferred name, phone, emergency contact, bank details for payroll, and tax
withholding basics. Tell Copilot in Teams what's wrong and what it should be — the assistant
structures the change (current value → proposed value), asks you to confirm, and files it with
the owning data team.

## Service levels

Address and contact changes: 3 business days. Name changes: 5 business days (documentation
required — certificate or court order). Bank details: verified by a micro-deposit before the
switch, so allow one payroll cycle.

## Why corrections matter

Letters, benefits, tax forms, and payroll all read the same worker record. A wrong address can
delay your tax documents; wrong bank details delay pay. Fixing it once at the source fixes it
everywhere downstream.

## Privacy

Sensitive values are detected and handled by the PII tokenizer plane — your data travels
masked, and every change is written to the audit ledger with who approved it.
