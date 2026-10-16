# GitLab Certified CI/CD Associate — Portable

A self-hosted study bot for the **GitLab Certified CI/CD Associate** exam: practice questions with explanations, a Claude tutor that draws the pipeline with official icons when you get one wrong, a weekly readiness report, and a web front end through [Exam Portal](https://github.com/gcjk768/exam-portal) (quiz, timed 50-question mock exam, reading list by domain).

> Unofficial and independent. Not affiliated with GitLab. The questions are community-written practice items, not exam content.

## The exam (checked 2026-10-16)

50 multiple-choice and multiple-response questions, 75 minutes, pass 75%, USD 150, online and unproctored, two attempts within a 14-day window, no expiry. Domains: YAML Configuration 22%, Pipeline Development 18%, CI/CD Fundamentals 18%, Troubleshooting & Optimization 14%, Container & Package Management 12%, Security Integration 8%, Runner Configuration 8%. There is no hands-on lab in the current version.

## Question bank

`build_csv.py` parses files downloaded into `sources/online/` (not redistributed) and any authored banks in `banks/`:

| Source | Questions | Licence |
|---|---|---|
| smshack/MYNOTE practice exam sets 1 to 8 | 400 | no licence, personal study only |
| rebash-academy CI/CD fundamentals quiz | 40 | MIT |
| open-exam-prep.com sample | 1 | site content |

Questions are tagged with the official domain where the source names it, else by keyword. The bot's score weights are the official domain weights.

## Setup

Same as the [SAP-C03 bot](https://github.com/gcjk768/aws-certified-solutions-architect-professional-portable): BotFather token in `bot.env`, `python -I build_csv.py`, `python test_bot.py`, then `docker compose up -d --build` or `.\run.ps1`.

## License

MIT for the code.
