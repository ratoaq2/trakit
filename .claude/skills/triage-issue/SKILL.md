---
name: triage-issue
description: Label a GitHub issue and draft a reply to the reporter. Use to triage, label, classify, or reply to issues.
---

# Triage an issue

Goal: each open issue has the correct labels and, when necessary, a reply that asks for the missing
information.

## Steps

1. Read the issue and its comments: `gh issue view <n> --comments`.
2. Check that the labels below still exist: `gh label list`. If they do not match, tell the user and
   update this file.
3. Decide the labels (see the table below). Use one type label: `bug`, `enhancement`, `documentation`,
   or `question`. Add the other labels only when they apply.
4. Check if a bug has enough information: the trakit version, the Python version, the input title or
   file name, the command or code, the actual output, and the expected output.
5. Draft a reply in strict STE100 (`writing-style` skill). Ask for each missing item in a separate
   sentence.
6. Show the labels and the reply to the user. **Wait for approval.** Then run
   `gh issue edit <n> --add-label ... --remove-label ...` and `gh issue comment <n> --body-file <file>`.
7. If the user wants to start work, continue with the `investigate` skill.

## Labels

| Label | Use when |
| --- | --- |
| `bug` | The guess is wrong and someone can reproduce it with an input title. |
| `enhancement` | A new capability, for example a new word or a new property. |
| `documentation` | README or other documentation. |
| `question` | The reporter asks how trakit works. No change is needed yet. |
| `duplicate` | Another issue has the same problem. Link to it in the reply. |
| `invalid` | The issue is not about trakit. |
| `wontfix` | We do not change this. Give the reason in the reply. |
| `good first issue` | A small change with a clear test case. |
| `help wanted` | We want a pull request from a contributor. |

Dependabot uses `dependencies`, `github_actions`, `python`, and `python:uv`. Do not use them for issues.

## Many issues

For a review of all open issues, run `gh issue list --state open --limit 100`. Make a table: number,
title, current labels, suggested labels, and one line on the next action. Do not change labels until the
user approves the table.
