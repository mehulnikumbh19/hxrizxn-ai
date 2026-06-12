# Pre-Publish / Pre-Push Checklist

Run through this **before every push to the public repository** and especially before the Agents League submission. Most items are one command.

## 1. No secrets are tracked

```powershell
# Should print NOTHING. If it prints .env, stop and fix.
git ls-files | Select-String "\.env$|\.env\."

# Should print NOTHING. Confirms .env is ignored.
git check-ignore .env; if ($LASTEXITCODE -ne 0) { "WARNING: .env is NOT ignored" }
```

If `.env` is ever tracked:

```powershell
git rm --cached .env
git commit -m "Stop tracking .env"
# Then ROTATE any keys it contained — assume they are compromised.
```

## 2. No secrets in history

```powershell
# Should print NOTHING.
git log --all --diff-filter=A --name-only --pretty=format: | Select-String "\.env$"
```

If `.env` (or any secret file) appears in history:

```powershell
pip install git-filter-repo
git filter-repo --path .env --invert-paths --force
# Force-push only if you understand the consequences and no one else has cloned.
```

## 3. No secret files committed

```powershell
# Should print NOTHING. Catches credential-style files.
git ls-files | Select-String "secret|cred|fedcred|\.key$|\.pem$|\.pfx$|token|password|\.db$|\.log$"
```

Known files that must stay **out** of the repo (already git-ignored): `.env`, `*.db`, `*.log`, `fedcred.json`.

## 4. No hardcoded keys in code

```powershell
# Should print NOTHING (markdown and .env files excluded).
git grep -nE "sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|api[_-]?key['""]?\s*[:=]\s*['""][A-Za-z0-9]{16,}" -- ':!*.md' ':!.env*'
```

## 5. No personal / sensitive demo data

- Confirm no real personal decision content, names, or private situations are in any committed file, README, or screenshot.
- Demo examples must be **generic** (e.g. a business or hypothetical decision), not a real person's private scenario.
- The runtime database (`*.db`) holds test prompts and must remain git-ignored.

## 6. `.env.example` is clean

```powershell
# Should print NOTHING — placeholders only, no real key values.
Select-String -Path .env.example -Pattern "KEY=.{12,}|sk-|https://[a-z0-9-]+\.openai\.azure\.com"
```

## 7. Attribution and account hygiene (Agents League requirements)

- Commits use an appropriate author email (not a confidential/employer address you don't want public):
  ```powershell
  git config user.email
  ```
- GitHub account has 2FA enabled.
- The Microsoft Contributor License Agreement (CLA) is signed when prompted.

---

**If every command above prints nothing (or the documented "OK"), the repo is safe to push and submit.**
