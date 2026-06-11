# Codex Skills

This repository tracks the installed Codex skills for this environment.

It is used as a local backup, audit trail, and update target for the skills
installed under `~/.codex/skills`.

## Contents

- `.system/` contains bundled system skills.
- `chatgpt-apps/`, `hatch-pet/`, and `playwright/` are synced from the
  OpenAI skills repository curated set.
- `paper-spine*` skills are synced from the PaperSpine Codex distribution.
- Other directories are locally installed or third-party skills that do not
  currently have a configured upstream source.

## Remotes

- `origin`: `https://github.com/sdoaiya/skills.git`
- `openai-skills`: `https://github.com/openai/skills.git`
- `paperspine`: `https://github.com/WUBING2023/PaperSpine.git`

`origin` is the push target for this aggregate repository. The other remotes
are upstream sources used for selective updates.

## Update Notes

Do not run a direct `git pull` from `openai-skills` or `paperspine` into this
repository. Their repository layouts differ from the installed skills layout.
Fetch them first, then selectively sync the matching skill directories.

The `.system` skills are intentionally not mirrored from the public OpenAI
repository unless reviewed manually, because the local bundled versions may
include extra assets or scripts.

## Verification

After updates, check:

```powershell
git status --short
Get-ChildItem -Path $env:USERPROFILE\.codex\skills -Recurse -Filter SKILL.md
```

Each skill should have a valid `SKILL.md` with YAML front matter containing
`name` and `description`.
