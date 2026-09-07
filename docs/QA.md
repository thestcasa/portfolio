# Final QA checklist

## Automated

- [x] `pytest -q`
- [x] `python -m compileall -q main.py portfolio_app`
- [x] every case-study slug renders
- [x] 404 handler renders
- [x] sitemap and robots render
- [x] contact validation rejects invalid data
- [x] contact delivery failure is visible and never reported as success
- [x] mocked contact delivery returns success
- [x] honeypot suppresses delivery

## Visual / responsive

- [ ] 1440px desktop: hero hierarchy, project diagrams, long case-study sections
- [ ] 1024px tablet: grids collapse without overflow
- [ ] 390px mobile: navigation remains available, project rows stack, forms remain usable
- [ ] no horizontal overflow
- [ ] portrait and SVGs preserve aspect ratio
- [ ] focus states remain visible
- [ ] reduced-motion mode removes transition movement

## Accessibility

- [ ] keyboard-only navigation through header, CTAs and form
- [ ] skip link visible on focus
- [ ] single H1 per page
- [ ] form labels mapped to controls
- [ ] invalid fields use `aria-invalid` + inline errors
- [ ] images have meaningful alt text; diagrams are described as diagrams
- [ ] contrast checked for body, muted text and blue links

## Production switch

- [ ] `RESEND_API_KEY` configured
- [ ] verified `CONTACT_FROM_EMAIL` configured
- [ ] real contact form submission arrives
- [ ] replying to the email targets the visitor (`Reply-To`)
- [ ] current CV opens from header/about
- [ ] production canonical URL is `https://alessandrocasadei.com`
- [ ] Open Graph image loads publicly
- [ ] sitemap is reachable at `/sitemap.xml`
- [ ] no old “MSc Student” hero or stale Telematica “Present” text remains

## Environment note

Automated application tests and Python compilation passed locally on 2026-09-07. Browser-level Playwright QA remains unchecked because the execution environment could not download the Chromium runtime; the production-switch checklist intentionally keeps those visual items open for review/deployment verification.
