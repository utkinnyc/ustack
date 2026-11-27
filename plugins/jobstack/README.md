# jobstack

jobstack helps with the job hunt in Claude Code. Today it does one thing: it tunes the
resume you already have for the job you're applying to.

```
/jobstack:resume
```

- **Uses your resume where it is.** Run it in a repo with Typst or LaTeX source and it
  edits that directly. Anywhere else, point it at a file or paste the text, and it hands
  back updated text.
- **Fit check.** Maps the posting's must-haves to your real experience (matched, partial,
  gap), says whether it's worth applying, and suggests small projects to close the gaps.
- **Concrete edits.** Proposes changes as *current → proposed*, each tied to the posting,
  and applies only the ones you approve.
- **Honest.** It never invents facts. Anything the posting wants that your resume doesn't
  show comes back as a question, not a new bullet.

## Install

```
/plugin marketplace add utkinnyc/ustack
/plugin install jobstack@ustack
```

**Requirements:** [Claude Code](https://claude.com/claude-code). To rebuild the PDF after
edits, [Typst](https://typst.app) or a LaTeX install, depending on your source.

## Skills

| Skill | What it does |
|---|---|
| `resume` | Tailors your existing resume to a job description: fit check, proposed edits with reasons, and rebuilds the PDF if it's Typst or LaTeX source. |
