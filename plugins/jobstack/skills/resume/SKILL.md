---
name: resume
description: Tailor the user's existing resume to a job description — map the posting's must-haves to their real experience, judge fit, and propose concrete edits (reworded bullets, reordering, what to cut or add). Works on Typst or LaTeX source in the repo, or on pasted text. Use when the user shares a job description or posting, asks to tailor, tune or review their resume or CV, asks "am I a fit for this role", "is this impressive", or wants help with resume bullets.
---

# Resume

The user already has a resume. Your job is to tune it for a specific job: say what should change and why, then make the changes they approve. Do not start a new resume from scratch unless they ask.

## 1. Find the resume

- **In a repo with resume source** (`*.typ`, or `*.tex` with a resume-like name or content): use it directly. Read the content file (e.g. `main.typ`, `resume.tex`); skip templates and fonts unless layout comes up.
- **Otherwise:** ask once — "Where's your resume? I can read a file or folder you point me to, or you can paste the text." If they paste text, work on the text and hand back updated text for them to put in place.
- If there's no job description yet, ask for it (text or link). Without one, do a general review using the bullet rules below.

## 2. Tailor to the job description

1. Pull out the posting's must-haves, nice-to-haves and repeated keywords.
2. Map each to the user's real experience: **matched**, **partial**, or **gap**.
3. **Fit check:** a one-line verdict (strong / reasonable / stretch), the strongest matches, the real gaps, and whether it's worth applying.
4. **Proposed changes**, most impactful first, each as *current → proposed* with a one-line reason tied to the posting:
   - reword bullets to use the posting's language **where it's true**;
   - reorder bullets or sections so the most relevant work leads;
   - cut or shrink what this role doesn't care about;
   - surface experience the user has but under-sells.
5. **Candidates:** things the posting wants that the resume doesn't show. List them as questions ("Have you done X? If so, I'd add…"). Never add them without a yes.
6. For real gaps, suggest 1–3 small, concrete projects that would close them.

Then ask which changes to apply. Apply them one at a time if the user wants to go through them ("one by one").

## 3. Rules

- **Never invent facts, skills or numbers.** Only reword what the user has done or confirmed.
- **Be direct** when asked "is this impressive?" or "am I a fit?": say what reads as strong, what doesn't, and why.
- **Don't commit** unless asked. Move removed material to an `archive` file rather than deleting it, if the repo has one or the user wants it.
- **Numbers:** keep real figures only if the user says they're safe to share; otherwise use rounded or relative ones ("millions of positions daily", "~1M events/day").

## Bullet rules

1. Start with a strong past-tense verb (present tense for the current role).
2. One line, or two full lines. Never a second line with only one or two words on it.
3. Say what was built, how, and the result, with a number where it can be defended.
4. Translate domain jargon into general engineering terms (mesh simplification → processing large 3D geometry datasets), or gloss a niche term in parentheses.
5. Merge thin bullets into one stronger story; cut generic ones ("wrote tests") unless they carry scale or impact.
6. Order bullets so each role reads as a story, not a task list. Lead with the work most relevant to the target role.

Section order for experienced engineers: Work Experience, then Education, then Skills. Drop coursework, and projects too unless they add something the work doesn't.

## Editing the source (Typst or LaTeX)

- Change content, not the template, unless asked. Match the file's existing helpers and style.
- After edits, **rebuild** (the repo's `Makefile`, `typst compile`, or `latexmk`), confirm it's **still one page**, and open the PDF so the user can see it. If the build tool isn't installed, say so and give the command.
- If edits push it past one page, propose what to trim rather than shrinking fonts or margins.
- Layout questions (spacing, fonts) come second to content. If asked: measure the rendered page rather than guessing, keep one spacing scale, and compare fonts by rendering the same page in 3–4 candidates side by side.
