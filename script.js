const copyButtons = document.querySelectorAll('.copy-btn');

function getTextFromTarget(selector) {
  const node = document.querySelector(selector);
  return node ? node.innerText.trim() : '';
}

copyButtons.forEach((button) => {
  button.addEventListener('click', async () => {
    const explicit = button.dataset.copy;
    const target = button.dataset.copyTarget;
    const fallback = button.parentElement?.querySelector('.copy-block')?.innerText?.trim() || '';
    const text = explicit || (target ? getTextFromTarget(target) : fallback);

    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
      const previous = button.textContent;
      button.textContent = 'Скопировано ✓';
      button.classList.add('copied');
      setTimeout(() => {
        button.textContent = previous;
        button.classList.remove('copied');
      }, 1400);
    } catch (error) {
      console.error('Ошибка копирования:', error);
    }
  });
});

const progressBar = document.getElementById('progressBar');
window.addEventListener('scroll', () => {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  progressBar.style.width = `${progress}%`;
});

const zipLinkInput = document.getElementById('zipLink');
const downloadBtn = document.getElementById('downloadBtn');

if (zipLinkInput && downloadBtn) {
  downloadBtn.addEventListener('click', () => {
    const link = zipLinkInput.value.trim();
    if (!link) {
      alert('Пока это заглушка: вставьте ссылку на ZIP в поле выше.');
      return;
    }
    window.open(link, '_blank', 'noopener,noreferrer');
  });
}
