// Inquiry text stays in this browser tab; calculator rates never come from this handoff.
export const HANDOFF_KEY = 'miyabiya-pr-quote-contact-v1';
export const HANDOFF_TTL = 30 * 60 * 1000;
export const CONTACT_PATH = '/contact/?type=pr&from=estimate#contact-form';
export const MAX_CONTACT_TEXT = 5000;

export function contactText(summary) {
  if (typeof summary !== 'string' || !summary.trim()) throw new Error('Empty quote summary');
  let body = summary;
  let omittedQuoteUrl = false;
  // A long encoded share URL can exceed the form limit even though the complete
  // itemized summary fits. Keep every quote line and request; omit only that URL.
  if (body.length > MAX_CONTACT_TEXT) {
    const lines = body.split('\n');
    try {
      const url = new URL(lines.at(-1));
      if (url.origin === 'https://studio.msyn.me' && url.pathname === '/pricing/') {
        lines.pop();
        body = lines.join('\n') + '\n見積もりURLは別途共有できます。';
        omittedQuoteUrl = true;
      }
    } catch {}
  }
  if (body.length > MAX_CONTACT_TEXT) throw new Error('Quote summary exceeds form limit');
  return {body, omittedQuoteUrl};
}

export function saveHandoff(storage, origin, summary, now = Date.now()) {
  const text = contactText(summary);
  const record = {version:1, origin, createdAt:now, ...text};
  storage.setItem(HANDOFF_KEY, JSON.stringify(record));
  return record;
}

export function takeHandoff(storage, origin, now = Date.now()) {
  const raw = storage.getItem(HANDOFF_KEY);
  if (raw == null) return null;
  storage.removeItem(HANDOFF_KEY);
  try {
    const value = JSON.parse(raw);
    if (value.version !== 1 || value.origin !== origin || !Number.isFinite(value.createdAt)
      || value.createdAt > now || now - value.createdAt > HANDOFF_TTL
      || typeof value.body !== 'string' || !value.body.trim() || value.body.length > MAX_CONTACT_TEXT
      || typeof value.omittedQuoteUrl !== 'boolean') return null;
    return value;
  } catch { return null; }
}

export function receiveHandoff(doc, address, storage, now = Date.now()) {
  const url = new URL(address);
  if (url.pathname !== '/contact/' || url.searchParams.get('from') !== 'estimate') return false;
  const form = doc.getElementById('inquiry-form');
  const status = doc.getElementById('quote-handoff-status');
  if (!form || !status) return false;
  let saved;
  try { saved = takeHandoff(storage, url.origin, now); } catch {}
  if (!saved) {
    status.textContent = form.elements.body.value.trim() ? '入力中のご相談内容を保持しています。'
      : '見積もり内容を引き継げませんでした。見積もり画面で相談文をコピーして、ご相談内容へ貼り付けてください。';
    return false;
  }
  // Do not overwrite a form restored by the browser or already edited by its owner.
  if (form.elements.body.value.trim()) {
    status.textContent = '入力中のご相談内容を保持しました。見積もり内容は、見積もり画面からコピーして追記できます。';
    return false;
  }
  form.elements.kind.value = 'PR・タイアップのご依頼';
  form.elements.body.value = saved.body;
  status.textContent = '見積もり内容を入力しました。製品名・公開時期・お名前などを追記し、内容を確認して送信してください。'
    + (saved.omittedQuoteUrl ? '長い共有URLは省き、金額・明細・ご希望を引き継いでいます。' : '');
  return true;
}

export function installQuoteContact(doc, win) {
  doc.addEventListener('click', async event => {
    const control = event.target.closest('[data-quote-inquiry], [data-quote-copy]');
    if (!control) return;
    const host = control.closest('[data-quote-contact]');
    const field = host?.querySelector('[data-quote-text]');
    const status = host?.querySelector('[data-quote-status]');
    if (!field || !status) return;
    if (control.hasAttribute('data-quote-inquiry')) {
      try { saveHandoff(win.sessionStorage, win.location.origin, field.value); }
      catch {
        event.preventDefault();
        status.textContent = '見積もり内容を引き継げませんでした。表示した相談文をコピーし、PRの相談フォームへ貼り付けてください。';
        field.hidden = false;
        field.focus();
        field.select();
        const fallback = host.querySelector('[data-quote-fallback]');
        if (fallback) fallback.hidden = false;
      }
      return;
    }
    event.preventDefault();
    let text;
    try { text = contactText(field.value).body; }
    catch { text = field.value; }
    try {
      await win.navigator.clipboard.writeText(text);
      status.textContent = '相談文をコピーしました。フォームやメールに貼り付けてご利用ください。';
    } catch {
      field.value = text;
      field.hidden = false;
      field.focus();
      field.select();
      status.textContent = '下の相談文をコピーしてご利用ください。';
    }
  });
  const receive = () => {
    try { receiveHandoff(doc, win.location.href, win.sessionStorage); }
    catch {
      const url = new URL(win.location.href),status = doc.getElementById('quote-handoff-status');
      if (url.pathname === '/contact/' && url.searchParams.get('from') === 'estimate' && status) {
        status.textContent = '見積もり内容を引き継げませんでした。見積もり画面で相談文をコピーして、ご相談内容へ貼り付けてください。';
      }
    }
  };
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', receive, {once:true});
  else receive();
}

if (typeof document !== 'undefined' && typeof window !== 'undefined') installQuoteContact(document, window);
