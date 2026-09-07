(() => {
  const form = document.querySelector('.contact-form');
  if (!form) return;

  const API_URL = 'https://alessandro-casadei.onrender.com/api/contact';
  const submit = form.querySelector('button[type="submit"]');

  const topic = new URLSearchParams(window.location.search).get('topic');
  if (['hiring', 'consulting', 'collaboration', 'other'].includes(topic)) {
    const select = form.querySelector('[name="inquiry_type"]');
    if (select) select.value = topic;
  }

  function clearErrors() {
    form.querySelectorAll('.field-error[data-client-error="true"]').forEach((node) => node.remove());
    form.querySelectorAll('[aria-invalid="true"]').forEach((node) => node.removeAttribute('aria-invalid'));
  }

  function showStatus(type, text) {
    let status = document.querySelector('[data-contact-status]');
    if (!status) {
      status = document.createElement('div');
      status.dataset.contactStatus = 'true';
      status.setAttribute('role', 'status');
      form.parentNode.insertBefore(status, form);
    }
    status.className = `form-status form-status-${type}`;
    status.textContent = text;
    status.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function showErrors(errors) {
    Object.entries(errors || {}).forEach(([name, message]) => {
      const input = form.elements.namedItem(name);
      if (!input || !message) return;
      input.setAttribute('aria-invalid', 'true');
      const error = document.createElement('p');
      error.className = 'field-error';
      error.dataset.clientError = 'true';
      error.textContent = message;
      input.insertAdjacentElement('afterend', error);
    });
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    clearErrors();
    submit.disabled = true;
    const originalText = submit.textContent;
    submit.textContent = 'Sending…';

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      });
      const payload = await response.json().catch(() => ({}));

      if (!response.ok || !payload.ok) {
        showErrors(payload.errors);
        showStatus('error', payload.message || 'The message could not be sent. Please email me directly instead.');
        return;
      }

      form.reset();
      showStatus('success', payload.message || 'Message sent. I’ll reply to the email address you provided.');
    } catch (_error) {
      showStatus('error', 'The message could not be sent. Please email me directly instead.');
    } finally {
      submit.disabled = false;
      submit.textContent = originalText;
    }
  });
})();
