// Progress bar
const progressBar = document.getElementById('progressBar');
window.addEventListener('scroll', () => {
  const doc = document.documentElement;
  const scrollTop = doc.scrollTop || document.body.scrollTop;
  const scrollHeight = doc.scrollHeight - doc.clientHeight;
  const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
  progressBar.style.width = `${progress}%`;
});

// Copy helpers
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (e) {
    // Fallback (older iOS)
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    return ok;
  }
}

function toast(btn, ok) {
  const old = btn.textContent;
  btn.textContent = ok ? 'Скопировано ✅' : 'Не получилось';
  btn.disabled = true;
  setTimeout(() => {
    btn.textContent = old;
    btn.disabled = false;
  }, 900);
}

// Copy buttons
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.copy-btn');
  if (!btn) return;

  const direct = btn.getAttribute('data-copy');
  const targetSel = btn.getAttribute('data-copy-target');

  if (direct) {
    const ok = await copyText(direct);
    toast(btn, ok);
    return;
  }

  if (targetSel) {
    const node = document.querySelector(targetSel);
    if (!node) return toast(btn, false);

    // collect all .copy-block inside target OR all text inside target
    const blocks = node.querySelectorAll('.copy-block');
    let text = '';
    if (blocks.length) {
      text = Array.from(blocks).map(n => n.textContent.trim()).join('\n\n');
    } else {
      text = node.textContent.trim();
    }
    const ok = await copyText(text);
    toast(btn, ok);
  }
});

// Download link activator
const zipLink = document.getElementById('zipLink');
const downloadBtn = document.getElementById('downloadBtn');

function setDownloadState() {
  const url = (zipLink?.value || '').trim();
  const ok = /^https?:\/\/.+/i.test(url);
  if (ok) {
    downloadBtn.classList.add('ready');
    downloadBtn.textContent = 'Скачать пакет';
  } else {
    downloadBtn.classList.remove('ready');
    downloadBtn.textContent = 'Скачать пакет (заглушка)';
  }
}

zipLink?.addEventListener('input', setDownloadState);
setDownloadState();

downloadBtn?.addEventListener('click', () => {
  const url = (zipLink?.value || '').trim();
  if (!/^https?:\/\/.+/i.test(url)) {
    alert('Вставьте ссылку на ZIP (начинается с http/https).');
    return;
  }
  window.open(url, '_blank', 'noopener,noreferrer');
});
