# Static frontend deployment

The production portfolio is designed to run as a Render Static Site, with the existing free FastAPI Web Service retained only for contact delivery.

## Target topology

- `alessandrocasadei.com` -> Render Static Site / CDN
- `alessandro-casadei.onrender.com/api/contact` -> existing FastAPI service
- Resend environment variables remain only on the FastAPI service

This removes the Render free Web Service cold start from normal page loads. A cold start can still occur when a visitor submits the contact form after the API has been idle.

## Create the Static Site

Use the repository's `render.yaml` Blueprint. It creates `alessandro-casadei-static` with:

- build command: `python -m pip install -r requirements.txt && python scripts/build_static.py`
- publish path: `./dist`
- auto deploy after checks pass
- production security headers

Before moving the custom domain, verify these routes on `https://alessandro-casadei-static.onrender.com`:

- `/`
- `/work`
- `/consulting`
- `/about`
- `/contact`
- at least one `/work/<slug>` case study
- `/robots.txt`
- `/sitemap.xml`

Then submit a real contact-form message and verify delivery + Reply-To.

## Cut over the domain

After the preview passes:

1. remove `alessandrocasadei.com` from the old Web Service;
2. add `alessandrocasadei.com` to `alessandro-casadei-static`;
3. verify TLS and both root/www behaviour;
4. leave the old Web Service running on its `onrender.com` URL for `/api/contact`.

Do not delete the old Web Service while the contact form uses it.

## Rollback

If the static deployment has a problem, move `alessandrocasadei.com` back to the original Web Service. The FastAPI application continues to render the full portfolio and retains the original `/contact` POST route, so rollback does not require reverting code first.
