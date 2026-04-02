# Personal Portfolio — FastAPI + Jinja2 SSR

## Project Structure

```
portfolio/
├── main.py                  # FastAPI app: routes, form handling, data loading
├── data.json                # All content: bio, experience, projects, education
├── requirements.txt         # Python dependencies
├── templates/
│   ├── base.html            # Layout: nav, footer, Tailwind CDN, global styles
│   └── index.html           # Full portfolio page (extends base.html)
└── static/
    ├── style.css            # Optional custom CSS overrides
    └── cv.pdf               # Drop your PDF resume here
```

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

## Customisation

- **Content**: Edit `data.json` only — no Python or HTML changes needed.
- **Styling**: Tailwind utility classes in `index.html`; global tokens in `base.html`'s `<script>` block.
- **Contact form**: Replace the `print()` in `main.py`'s `/contact` route with `fastapi-mail` or any SMTP library.
- **Resume PDF**: Drop your `cv.pdf` into `static/` — the nav button links to it automatically.

## Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

For a production setup, consider adding gunicorn as the process manager:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```