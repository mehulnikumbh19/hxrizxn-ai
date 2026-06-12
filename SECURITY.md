# Security Policy

## Reporting a Vulnerability

If you discover a security issue in this project, please report it responsibly:

- **Do not** open a public issue for sensitive security reports.
- Open a GitHub Security Advisory on this repository, or contact the maintainer directly.
- Please include steps to reproduce and the potential impact.

We will acknowledge reports promptly and work to address valid issues.

## Secrets and Credentials

This project never stores secrets in the repository.

- All credentials (Azure OpenAI keys, Azure AI Search / Foundry IQ keys, OpenAI keys, database passwords) are loaded from a local `.env` file that is **git-ignored** and must never be committed.
- `.env.example` contains placeholder values only and documents the required variables.
- In production, secrets are injected as environment variables (Azure Container App secrets / GitHub Actions secrets), not baked into images or code.

If you believe a secret has been exposed in this repository or its history:

1. **Rotate the affected credential immediately** in the relevant portal (Azure OpenAI, Azure AI Search, OpenAI, etc.). Rotation is the only reliable remediation once a key has been exposed.
2. Remove the secret from tracking (`git rm --cached <file>`), and from history if necessary (`git filter-repo --path <file> --invert-paths`).
3. Report it via a Security Advisory so maintainers are aware.

## Handling User and Demo Data

Hxrizxn AI analyzes personal decisions, which can include sensitive or emotional topics.

- **No real personal data, PII, or private decision content is committed to this repository.** The runtime database (`*.db`) is git-ignored.
- Knowledge-base documents in `demo-data/` are generic, non-personal reference material only.
- Demo prompts and screenshots used in documentation or submissions must use **generic, non-identifying examples** — never a real person's private situation.

## Supported Configuration

This project targets the Microsoft Agents League and follows the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/)
and Microsoft Open Source GitHub guidelines. Contributions must contain only
General-level information suitable for public release.
