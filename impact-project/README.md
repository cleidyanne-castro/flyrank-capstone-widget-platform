# Impact Project

## Purpose

This note defines a repeatable maintenance loop for the portfolio. It turns the next finished project into a public case study instead of leaving the portfolio unchanged after the initial launch.

## Next case study

The next piece is the LLM Usage Metering and Billing Service in `../llm-metering/`. It complements the data engineering focus by turning model usage into auditable events. It also demonstrates tenant isolation, quotas, idempotency, and safe handling of billing data.

## Exact publishing target

The case study will be added to the `Featured projects` section of the portfolio repository:

https://github.com/cleidyanne-castro/cleidyanne-castro

The entry will be placed after the existing featured project entries in `README.md` and will include:

1. Problem: what usage or billing risk the service addresses.
2. Work: the ingestion, metering, quota, and tenant isolation decisions.
3. Result: a measured test result, a reproducible example, or a named limitation.

## Completion checklist

- The LLM metering project has a stable README and reproducible test command.
- The case study text names the implementation files and the verification result.
- The new entry is added to the portfolio repository under `Featured projects`.
- The entry links to the public project repository.
- The portfolio README is checked after the edit.
- The next review reminder is scheduled for the following month.

## Working context

The Claude Project containing the writing voice, stack, and identity kit is preserved separately. This repository contains no private prompts, credentials, or account data. The same project should be used when drafting the next case study so the portfolio remains consistent.

## Reminder

`reminder.ics` is an importable monthly calendar event. It points to this file and includes a one day display alarm. Importing it into a calendar is a separate action. `EVIDENCE.md` records what is present in this repository and what still requires a calendar import.

## Evidence

See `EVIDENCE.md` for the requirement-to-evidence matrix and the exact reviewer checks.
