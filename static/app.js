let currentMood = 'neutral';
let currentNewsId = null;
let currentModel = '';

const grid = document.getElementById('newsGrid');
const modal = document.getElementById('newsModal');
const modalTitle = document.getElementById('modalTitle');
const originalText = document.getElementById('originalText');
const rewrittenText = document.getElementById('rewrittenText');
const sourceLink = document.getElementById('sourceLink');
const loader = document.getElementById('loader');
const rewrittenTitle = document.getElementById('rewrittenTitle');
const modelSelect = document.getElementById('modelSelect');

const moodLabels = {
    neutral: '🧐 Нейтрально',
    joyful: '😊 Радостно',
    sad: '😢 Грустно',
    ironic: '🤡 Иронично'
};

async function fetchModels() {
    const res = await fetch('/api/models');
    const models = await res.json();
    modelSelect.innerHTML = '';
    
    if (models.length === 0) {
        modelSelect.innerHTML = '<option>Нет доступных моделей</option>';
        return;
    }

    models.forEach(m => {
        const option = document.createElement('option');
        option.value = m;
        option.innerText = m;
        modelSelect.appendChild(option);
    });

    // По умолчанию выбираем gemini-1.5-flash, если он есть
    if (models.includes('models/gemini-1.5-flash')) {
        modelSelect.value = 'models/gemini-1.5-flash';
    }
    currentModel = modelSelect.value;
}

async function fetchNews() {
    const res = await fetch('/api/news');
    const news = await res.json();
    grid.innerHTML = '';
    
    news.forEach(item => {
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <span class="card-source">${item.source_name}</span>
            <h3 class="card-title">${item.title}</h3>
            <p class="card-text">${item.original_text}</p>
        `;
        card.onclick = () => openModal(item);
        grid.appendChild(card);
    });
}

async function openModal(item) {
    currentNewsId = item.id;
    modalTitle.innerText = item.title;
    originalText.innerText = item.original_text;
    sourceLink.href = item.source_url;
    
    rewrittenText.classList.add('hidden');
    loader.classList.remove('hidden');
    rewrittenText.innerText = '';
    
    modal.classList.remove('hidden');
    
    await loadRewrittenText(item.id, currentMood, currentModel);
}

async function loadRewrittenText(id, mood, model) {
    rewrittenTitle.innerText = `Текст (${moodLabels[mood]})`;
    loader.classList.remove('hidden');
    rewrittenText.classList.add('hidden');
    
    const res = await fetch(`/api/news/${id}/rewrite?mood=${mood}&model=${model}`, { method: 'POST' });
    const data = await res.json();
    
    rewrittenText.innerText = data.text;
    loader.classList.add('hidden');
    rewrittenText.classList.remove('hidden');
}

document.querySelectorAll('.mood-btn').forEach(btn => {
    // Исключаем select из этого обработчика
    if(btn.tagName === 'BUTTON') {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mood-btn').forEach(b => {
                if(b.tagName === 'BUTTON') b.classList.remove('active');
            });
            btn.classList.add('active');
            currentMood = btn.dataset.mood;
            
            if (!modal.classList.contains('hidden') && currentNewsId) {
                loadRewrittenText(currentNewsId, currentMood, currentModel);
            }
        });
    }
});

modelSelect.addEventListener('change', () => {
    currentModel = modelSelect.value;
    if (!modal.classList.contains('hidden') && currentNewsId) {
        loadRewrittenText(currentNewsId, currentMood, currentModel);
    }
});

document.getElementById('closeModal').addEventListener('click', () => {
    modal.classList.add('hidden');
});

document.getElementById('parseBtn').addEventListener('click', async () => {
    const btn = document.getElementById('parseBtn');
    btn.innerText = 'Обновление...';
    btn.disabled = true;
    await fetch('/api/parse', { method: 'POST' });
    await fetchNews();
    btn.innerText = 'Обновить ленту';
    btn.disabled = false;
});

// Инициализация
document.querySelector('button[data-mood="neutral"]').classList.add('active');
fetchModels();
fetchNews();