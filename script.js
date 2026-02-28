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

(function () {
  const $ = (id) => document.getElementById(id);

  const money = (n) => {
    if (!isFinite(n)) return "—";
    return Math.round(n).toLocaleString("ru-RU") + " ₽";
  };
  const pct = (n) => (isFinite(n) ? (n * 100).toFixed(1) + "%" : "—");

  function calc() {
    const checks = +$("c_checks")?.value || 0;
    const avg = +$("c_avg")?.value || 0;
    const days = +$("c_days")?.value || 30;

    const cogs = (+$("c_cogs")?.value || 0) / 100;
    const acq = (+$("c_acq")?.value || 0) / 100;
    const del = (+$("c_del")?.value || 0) / 100;
    const taxRate = (+$("c_tax")?.value || 0) / 100;

    const payroll = +$("c_payroll")?.value || 0;
    const rent = +$("c_rent")?.value || 0;
    const utils = +$("c_utils")?.value || 0;
    const mkt = +$("c_mkt")?.value || 0;
    const other = +$("c_other")?.value || 0;

    const revDay = checks * avg;
    const revMonth = revDay * days;

    const varRate = cogs + acq + del;
    const varCost = revMonth * varRate;
    const gross = revMonth - varCost;

    const fixed = payroll + rent + utils + mkt + other;
    const op = gross - fixed;

    const tax = revMonth * taxRate;
    const net = op - tax;

    const cm = 1 - varRate;
    const beRev = cm > 0 ? fixed / cm : Infinity;
    const beChecksDay = (beRev / days) / (avg || 1);

    $("o_rev_m").textContent = money(revMonth);
    $("o_rev_d").textContent = money(revDay);
    $("o_var").textContent = money(varCost);
    $("o_gross").textContent = money(gross);
    $("o_fixed").textContent = money(fixed);
    $("o_op").textContent = money(op);
    $("o_tax").textContent = money(tax);
    $("o_net").textContent = money(net);
    $("o_cm").textContent = pct(cm);
    $("o_be_checks").textContent = isFinite(beChecksDay) ? Math.ceil(beChecksDay) + " чек/день" : "—";
  }

  const btn = $("calcBtn");
  if (btn) btn.addEventListener("click", calc);

  const reset = $("calcReset");
  if (reset) reset.addEventListener("click", () => location.reload());

  ["c_checks","c_avg","c_days","c_cogs","c_acq","c_del","c_payroll","c_rent","c_utils","c_mkt","c_other","c_tax"]
    .forEach(id => $(id)?.addEventListener("input", () => calc()));

  if ($("calcBtn")) calc();
})();
