# Architecture and product direction

## Product position

Primary identity: **AI, Data & Automation Engineer**.

The website is designed to prove four things quickly:

1. Alessandro can build software systems around AI, not only notebooks.
2. He understands evaluation, data quality and failure modes.
3. He has hands-on context in operational / RevOps automation.
4. There are clear paths for both hiring and consulting without splitting the site into two artificial brands.

## Information architecture

```text
/
├── work
│   └── work/{project}
├── consulting
├── about
└── contact
```

Recruiter path: home → selected work → about/CV → contact.

Client path: home → consulting → contact, with public engineering work used as the current credibility layer until real external consulting case studies exist.

## Why FastAPI + Jinja stays

The previous implementation had the right deployment primitive but the wrong product structure.

A migration to a static-first framework was considered, but the benefits did not justify the change:

- the site already needs a server for contact delivery;
- Jinja produces simple, crawlable HTML with no hydration cost;
- content volume is still small enough that JSON + templates is maintainable;
- retaining the app entry point lowers production-switch risk;
- a custom CSS system is sufficient for the intended visual direction.

The redesign therefore modernizes the existing stack rather than replacing it.

## Visual system

Direction: **technical editorial dossier**.

The visual language uses:

- warm paper background, black rules and one signal-blue accent;
- large serif statements paired with compact mono labels;
- square edges and explicit grid/rule structure instead of rounded component cards;
- project-specific diagrams derived from actual architecture/evaluation paths;
- restrained hover motion only;
- no decorative gradients, glass, particles, fake terminal UI or neural-network imagery.

The project rows are the primary visual objects. The site is designed around evidence rather than a reusable card component.

## Contact architecture

`POST /contact` validates a typed payload and sends through Resend.

No database is added because the initial requirement is delivery, not lead management. The provider configuration remains external through environment variables.

Current controls:

- Pydantic validation + EmailStr;
- honeypot;
- small in-memory rate limiter;
- HTML escaping;
- explicit Reply-To;
- idempotency key;
- honest provider/configuration failure state.

The rate limiter is intentionally modest. If the site later receives enough abuse to justify shared state, replace it with a Cloudflare/WAF limit or a distributed store rather than prematurely adding a database.

## SEO / performance

- semantic multi-page SSR;
- page-specific title, description and canonical URL;
- Open Graph / Twitter metadata;
- Person + CreativeWork JSON-LD;
- sitemap + robots;
- static SVG diagrams;
- no client-side framework or animation library;
- no third-party font or analytics request by default;
- security headers and static caching.
