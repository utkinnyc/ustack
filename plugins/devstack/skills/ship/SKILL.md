---
name: ship
description: Ship the current work in any repo — run devstack:review, commit only the files the change needs with conventional messages, push a branch, and open a PR whose body says what the request was, what changed and how it was checked. Includes an optional Docker → Railway deploy workflow for apps made with devstack:scaffold. Use when the user says ship it, commit and push, open a PR, or /devstack:ship.
---

# Ship

Get finished work onto GitHub through a PR. Never push to `main` directly. Invoking this skill is the user's go-ahead to commit, push and open the PR; it is not a go-ahead to merge.

## Flow

1. **Review.** Run `devstack:review`. If it reports `blocked`, stop and say why.
2. **Branch.** If on the default branch, create one named after the change (`feat/<slug>`, `fix/<slug>`). Otherwise stay on the current one.
3. **Commit.** Stage specific paths (`git add <paths>`), never `git add -A` blindly, and never `.env`, databases or build output. Leave unrelated changes out and mention them. One concern per commit, with a conventional subject (`feat:`, `fix:`, `docs:`, `chore:`; `!` after the type or scope for a breaking change, e.g. `feat(api)!:`). End messages with the attribution Claude Code asks for, if any.
4. **Push.** `git push -u origin <branch>`.
5. **Open the PR.** Write the body to a file and use `gh pr create --title "<conventional title>" --body-file <file>`. Never pass the body inline: backticks in it run as shell commands. The body:

   ```markdown
   ## Why
   <the request, in one or two lines>

   ## What changed
   - <one bullet per meaningful change>

   ## How it was checked
   - <the "done when" check and its result; the project checks that ran>

   ## Not changed
   - <things noticed and left alone, if any>
   ```

   Don't write `@name` mentions. End with the line Claude Code asks for, if any.
6. **Report** the PR URL. If the repo has a version-bump or release workflow keyed on the PR title, say which bump the title gives.

Don't merge the PR; the user does. If push or `gh` fails on auth, report the exact error and stop.

## Deploy workflow (apps made with `devstack:scaffold`)

If `.github/workflows/deploy.yml` doesn't exist, offer this one and ask before adding it. It builds the image to catch Docker failures, then deploys to Railway. It needs a `RAILWAY_TOKEN` repo secret (`gh secret set RAILWAY_TOKEN`), a `RAILWAY_SERVICE` variable (`gh variable set RAILWAY_SERVICE`) and a Railway service with a volume at `/data`. For a VPS instead, use `devstack:go-live`.

```yaml
name: deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t app:${{ github.sha }} .
      - name: Deploy to Railway
        run: npx --yes @railway/cli up --ci --service "$RAILWAY_SERVICE"
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
          RAILWAY_SERVICE: ${{ vars.RAILWAY_SERVICE }}
```

After merge, watch it with `gh run list --limit 3` then `gh run watch <id>`, or `gh run view --log-failed` on failure.
