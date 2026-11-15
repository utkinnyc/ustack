---
name: scaffold
description: Bootstrap a new small web app with the shipstack stack (TypeScript, Next.js App Router, plain CSS, node:sqlite, single Node 24 Docker container) and create a private GitHub repo. Use when the user wants to start a new app or says /scaffold.
---

# Scaffold

Create a new app from nothing in one pass. Write each file once. Ask only for the app
name (kebab-case) and a one-line description if they are not already known. If
`docs/plan.md` exists, follow it. Do not run `create-next-app`; it adds things we do
not want.

## 1. Dependencies (the only ones)

`next`, `react`, `react-dom`, plus dev: `typescript`, `@types/node`, `@types/react`,
`@types/react-dom`. Nothing else without asking. Let
`npm install` pick current versions.

## 2. Files

- `package.json`: `"private": true`, `"type": "module"`, `"engines": {"node": ">=24"}`,
  scripts `dev` (`next dev`), `build` (`next build`), `start`
  (`node .next/standalone/server.js`), `typecheck` (`tsc --noEmit`).
- `tsconfig.json`: strict, `moduleResolution: "bundler"`, `jsx: "preserve"`, the `next`
  plugin, path alias `@/*` to `src/*`.
- `next.config.ts`:

```ts
import type { NextConfig } from "next";

const config: NextConfig = {
  output: "standalone",
};

export default config;
```

- `src/app/layout.tsx` (imports `./globals.css`, sets `<html lang="en">`),
  `src/app/page.tsx` (server component), `src/lib/db.ts` (opens `DATABASE_PATH`,
  default `/data/app.db`, creates tables with `IF NOT EXISTS`, using
  `DatabaseSync` from `node:sqlite`), `src/instrumentation.ts` (exports `register()`;
  start background jobs only when `process.env.NEXT_RUNTIME === "nodejs"`, via dynamic
  import so jobs never load in other runtimes).
- `src/app/globals.css`: system font stack, a few CSS variables for color and spacing,
  a readable max-width container, `prefers-color-scheme` dark variables. No resets
  library, no animations or transitions.
- `Dockerfile`:

```dockerfile
FROM node:24-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:24-slim
WORKDIR /app
ENV NODE_ENV=production PORT=3000 HOSTNAME=0.0.0.0 DATABASE_PATH=/data/app.db
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
VOLUME /data
EXPOSE 3000
CMD ["node", "server.js"]
```

- `.dockerignore`: `node_modules`, `.next`, `.git`, `.env*` (but not `.env.example`),
  `docs`, `*.db`.
- `.env.example`: `DATABASE_PATH=/data/app.db` and one commented line per variable.
- `.gitignore`: `node_modules`, `.next`, `.env`, `.env.local`, `*.db`, `next-env.d.ts`.
- `public/.gitkeep`, so the Dockerfile `COPY` of `public` never fails.
- `README.md`: name, one-line description, local run (`npm install`, `npm run dev`),
  env vars table, `docker build` and `docker run -v data:/data -p 3000:3000` commands,
  and a Deploy section ("see `.github/workflows/deploy.yml`", if present).

## 3. Verify and publish

1. `npm install`, then `npm run typecheck` and `npm run build`. Fix failures.
2. `git init -b main`, `git add -A`, commit `feat: scaffold <name>` ending with the line
   `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
3. `gh repo create <name> --private --source=. --push`. Never create a public repo
   unless the user says so.
4. Tell the user: repo URL, how to run it, and that deploy setup is in `ship`.

If `gh` is not signed in or Docker is missing, skip that step, say so, and continue.
