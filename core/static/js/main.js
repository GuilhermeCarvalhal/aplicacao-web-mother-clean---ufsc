document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Confirmar antes de remover
document.querySelectorAll('form[action*="deletar"]').forEach(form => {
    form.addEventListener('submit', function(e) {
        if (!confirm('Tem certeza que deseja remover esta tarefa?')) {
            e.preventDefault();
        }
    });
});

// Adicionar estado de loading
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.disabled) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processando...';
        }
    });
});

// Smooth scroll for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Abas e janela de leitura da página de componentes
const infoTabs = document.querySelectorAll('.info-tab');
const infoPanels = document.querySelectorAll('.info-tab-panel');
const readerModal = document.querySelector('#reader-modal');
const readerWindow = document.querySelector('.reader-window');
const readerTitle = document.querySelector('#reader-modal-title');
const readerContent = document.querySelector('#reader-modal-content');

infoTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetId = tab.dataset.tabTarget;
        infoTabs.forEach(item => {
            const selected = item === tab;
            item.classList.toggle('is-active', selected);
            item.setAttribute('aria-selected', selected);
        });
        infoPanels.forEach(panel => {
            const active = panel.id === targetId;
            panel.classList.toggle('is-active', active);
            panel.hidden = !active;
        });
    });
});

function closeReader() {
    if (!readerModal) return;
    readerModal.hidden = true;
    document.body.classList.remove('reader-is-open');
}

document.querySelectorAll('[data-reader-close]').forEach(button => {
    button.addEventListener('click', closeReader);
});

document.querySelectorAll('[data-reader-target]').forEach(button => {
    button.addEventListener('click', () => {
        if (!readerModal) return;
        const source = document.querySelector(`#${button.dataset.readerTarget} .reader-source`);
        const title = document.querySelector(`#${button.dataset.readerTarget} h3`);
        if (!source || !title) return;
        readerTitle.textContent = title.textContent;
        readerContent.innerHTML = source.innerHTML;
        readerModal.hidden = false;
        document.body.classList.add('reader-is-open');
        readerWindow.querySelector('.reader-close').focus();
    });
});

document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && readerModal && !readerModal.hidden) closeReader();
});