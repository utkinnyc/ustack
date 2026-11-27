# jobstack

jobstack helps with the job hunt in Claude Code. Today it does one thing well: your
resume, kept as code and tailored to the job you're applying for.

```
/jobstack:resume
```

- **Resume as code.** A Typst source (or a port from LaTeX) with a reproducible build and
  a dated PDF, laid out on one page with measured, consistent spacing.
- **Honest bullets.** Crisp, verb-first bullets in general engineering terms. It never
  invents facts: anything a job description suggests but you haven't confirmed goes on a
  separate list for you to accept or reject.
- **Tailoring and fit.** Matches the resume to a job posting, judges how well you fit,
  and suggests projects to close the gaps.

## Install

```
/plugin marketplace add utkinnyc/ustack
/plugin install jobstack@ustack
```

**Requirements:** [Claude Code](https://claude.com/claude-code) and
[Typst](https://typst.app) to build the PDF.

## Skills

| Skill | What it does |
|---|---|
| `resume` | Resume as Typst code: measured one-page layout, crisp honest bullets, tailoring and fit checks against a job description. |
