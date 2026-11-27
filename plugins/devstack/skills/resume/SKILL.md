---
name: resume
description: Build, typeset and tailor a software engineer's resume as code (Typst, or porting from LaTeX) — one-page layout with measured, consistent spacing, font comparisons, a reproducible build with a dated PDF — and rewrite the content into crisp, honest, verb-first bullets that translate domain jargon into general engineering terms and match a target job description. Also judges fit against a job posting and suggests projects to close gaps. Use this whenever the user mentions their resume or CV, a job description or posting, tailoring for a role, bullet points about their work, Typst or LaTeX resumes, resume fonts or spacing, or asks "is this impressive" or "should I put this number on my resume".
---

# Resume

Treat the resume as a small codebase with a strict output: one clean page that a recruiter and an engineer both understand.

## Working style

- **One change at a time** when the user is reviewing ("let's pick one by one"). After each change, rebuild, confirm it's still one page, and **open the PDF** so they can see it.
- **Don't commit** unless asked. Keep removed material (old projects, coursework) in an `archive` file instead of deleting it.
- **Never invent facts.** Turn what the user says into bullets. Anything a job description suggests but the user hasn't confirmed goes in a separate "candidates" list for them to accept or reject. If a bullet sounds copied from a teammate's resume, reword it in the user's own terms.
- Be direct when asked "is this impressive?": say what reads as strong, what doesn't, and why.

## The code side (Typst)

- Layout: `template.typ` (helpers: section, company, entry/role, skill, spacing scale) and `main.typ` (content only). Bundle fonts in `fonts/` with their licenses so it builds the same on any machine. Use a `Makefile` and, if wanted, a CI workflow that builds the PDF.
- Output a PDF named like `<Name>_Resume_<YYYY-MM>.pdf`, tracked in git if the user wants a history of what was sent.
- **Porting from LaTeX:** match the original layout first, then refactor. Verify a refactor by rendering before and after and comparing pixel by pixel.
- **Spacing:** measure the rendered page rather than guessing. Use one spacing scale: bullets < wrapped lines' gap < entries < companies < sections, with the gap under every section rule identical. Body text 10.5–11pt, margins about 0.4–0.5in, and the page filled to just above the bottom margin.
- **Fonts:** when asked, render the same resume in 3–4 candidates (e.g. IBM Plex Sans, Inter, Source Sans) side by side at print size, noting density and leftover space. Any normal font is fine for ATS, which reads the text layer.

## The content side

**Order:** Work Experience first for experienced engineers; then Education; Skills. Drop coursework, and projects too unless they add something the jobs don't.

**Bullet rules:**
1. Start with a strong past-tense verb (present tense for the current role).
2. One line, or two full lines. Never a second line with one or two words on it.
3. Say what you built, how, and the result, with a number where you can defend it.
4. Translate domain jargon into general engineering terms (e.g. mesh simplification → processing large 3D geometry datasets; a desk-specific system → "sell-side trading platform"), and gloss a niche term in parentheses if you keep it.
5. Merge thin bullets into one stronger story; cut generic ones ("wrote tests") unless they carry scale or impact.
6. Order bullets so the role reads as a story, not a task list.

**Numbers:** use real scale when it's allowed (events per second, positions per day, latency cut by X%). If figures are internal, use rounded or relative versions ("millions of positions daily", "~1M events/day") and check with the user what's safe to share. Lead with the most impressive work for the target role (e.g. migrations and real-time services for backend and distributed-systems roles).

**Titles and links:** keep titles consistent and honest across roles. Link company and product names to public pages if the user wants, applied uniformly.

## Tailoring to a job description

1. Pull out the JD's must-haves and keywords.
2. Map each to the user's real experience: matched, partially matched, or gap.
3. Reword existing bullets to use the JD's language where it's true. Don't add skills the user lacks.
4. **Fit check** (when asked "is this good for this role?"): give a verdict, the strongest matches, the gaps, and whether to apply. Change nothing unless asked.
5. For gaps, suggest 1–3 concrete portfolio projects that would close them.
