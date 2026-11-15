---
name: ship
description: Ship the current work: run review, commit with a conventional message, push a branch, and open a PR with gh. Includes a GitHub Actions workflow template that builds the Docker image and deploys to Railway. Use when the user says ship it, commit and push, open a PR, or /ship.
---

# Ship

Get finished work onto GitHub through a PR. Never push to `main` directly.

## Flow

1. **Review.** Invoke `review`. If it reports `blocked`, stop and tell the user.
2. **Branch.** If on `main`, create a branch named after the change
   (`feat/<slug>`, `fix/<slug>`). Otherwise stay on the current one.
3. **Commit.** Stage specific files (`git add <paths>`; never `git add -A` blindly, and
   never `.env` or `*.db`). Make small commits, one concern each, with a conventional
   subject: `feat:`, `fix:`, `docs:`, `chore:`. Every message ends with this line,
   after a blank line:

   ```
   Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
   ```
4. **Push.** `git push -u origin <branch>`.
5. **Open the PR.** `gh pr create --title "<conventional title>" --body "<body>"`.
   The body is a few bullets on what changed and why, plus how it was checked, and ends
   with the line `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
   Do not write `@name` mentions in commits or PR bodies.
6. **Report.** Give the PR URL. If `.github/workflows/deploy.yml` exists, say: deploys
   run on merge to `main`; watch with `gh run list --limit 3` then `gh run watch <id>`,
   or `gh run view --log-failed` on failure. If it does not exist, offer the template
   below and ask before adding it.

## Deploy workflow template

Save as `.github/workflows/deploy.yml`. It builds the image to catch Docker failures,
then deploys to Railway. Needs a `RAILWAY_TOKEN` repo secret (a Railway project token:
`gh secret set RAILWAY_TOKEN`) and a Railway service with a volume mounted at `/data`.

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

Set the service name with `gh variable set RAILWAY_SERVICE`. For another Docker host,
replace the last step and keep the build step.

## Rules

- Do not merge the PR; the user does.
- If the working tree has unrelated changes, leave them out and mention them.
- If pushing or `gh` fails on auth, report the exact error and stop.
