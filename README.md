# Alessandro Casadei — portfolio

Production portfolio for [alessandrocasadei.com](https://alessandrocasadei.com).

The site is intentionally **not** a single-page CV. It has two natural paths:

- hiring / recruiter evaluation: `/` → `/work` → `/about` / CV;
- consulting conversations: `/` → `/consulting` → `/contact`.

## Architecture decision

The redesign keeps **FastAPI + Jinja2 SSR** instead of migrating to Next.js or Astro.

Why:

- the current deployment already runs Python and the site needs one real server action (contact delivery);
- case studies are content-heavy and benefit from server-rendered, crawlable HTML;
- a framework migration would add a second deployment model or serverless contact function without creating meaningful product value;
- custom CSS gives more visual control than a Tailwind/component-library rebuild and removes the Tailwind CDN dependency;
- the result ships almost no client JavaScript and remains easy to inspect.

See `docs/ARCHITECTURE.md` for the fuller rationale.

## Routes

- `/` — positioning, selected work, consulting path, experience signal
- `/work` — selected case studies + smaller archive
- `/work/{slug}` — evidence-first project case studies
- `/consulting` — problem-led consulting positioning
- `/about` — experience, education, toolbox, CV
- `/contact` — recruiter/client form with real email delivery
- `/sitemap.xml`, `/robots.txt`, `/healthz`

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements-dev.txt
uvicorn main:app --reload
```

## Contact delivery

The form uses the **Resend HTTP API**. It does not store messages in a database.

Copy `.env.example` into your deployment environment and set:

```text
RESEND_API_KEY=...
CONTACT_FROM_EMAIL=Alessandro Casadei <website@alessandrocasadei.com>
CONTACT_TO_EMAIL=alessandroocasadei@gmail.com
```

`CONTACT_FROM_EMAIL` must use a sender/domain accepted by your Resend account. `Reply-To` is set to the visitor's validated email address.

Protection in the initial version:

- strict server-side validation;
- hidden honeypot;
- lightweight per-process rate limiting;
- HTML escaping before email rendering;
- Resend idempotency key;
- explicit error state when delivery is unavailable or rejected.

There is **no fake success path for real users**. If provider configuration is missing, the form tells the visitor to use the direct email link.

## Content

Public-facing content lives in `content/site.json` and the ordered records under `content/projects/`. Project claims were based on the actual repositories and are intentionally conservative:

- collaborative repositories are labelled as collaborative;
- academic leaderboard/benchmark results are described as academic results;
- projects without a trustworthy headline metric do not get one invented for them;
- architecture diagrams are explanatory diagrams, not fake screenshots.

## Tests

```bash
pytest -q
python -m compileall -q main.py portfolio_app
```

Tests cover page rendering, project routes, metadata, internal navigation, contact validation, delivery errors, the spam honeypot and the success path with a mocked provider.

## Deployment notes

The app entry point remains `main:app`, so an existing `uvicorn main:app ...` production command can stay in place.

Before switching production:

1. merge the redesign PR;
2. configure the Resend sender/domain and environment variables;
3. deploy the branch/merged commit;
4. send a real contact message and verify Reply-To;
5. run the QA checklist in `docs/QA.md` on the production URL.

Analytics are intentionally omitted by default. Add privacy-conscious analytics only if there is a real question to answer with the data.
