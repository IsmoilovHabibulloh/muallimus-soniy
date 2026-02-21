/**
 * Muallimi Soniy — Admin Panel Application
 * Single-page application with JWT authentication
 */

const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api/v1'
    : '/api/v1';

// ===== State =====
let authToken = localStorage.getItem('admin_token') || null;
let currentPage = 'dashboard';
let waveformZoom = 1;
let waveformAudioCtx = null;
let waveformSource = null;

// ===== Init =====
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        showDashboard();
        loadDashboardData();
    }

    // Event listeners
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('sidebar-toggle').addEventListener('click', toggleSidebar);
    document.getElementById('btn-import-pdf').addEventListener('click', triggerPdfImport);
    document.getElementById('pdf-input').addEventListener('change', handlePdfUpload);
    document.getElementById('btn-upload-audio').addEventListener('click', () => document.getElementById('audio-input').click());
    document.getElementById('audio-input').addEventListener('change', handleAudioUpload);
    document.getElementById('btn-publish').addEventListener('click', handlePublish);
    document.getElementById('telegram-form').addEventListener('submit', handleSaveTelegram);
    document.getElementById('btn-test-telegram').addEventListener('click', handleTestTelegram);
    document.getElementById('feedback-filter').addEventListener('change', loadFeedback);
    document.getElementById('playback-speed').addEventListener('input', updateSpeed);
    document.getElementById('page-image-input')?.addEventListener('change', handlePageImageUpload);

    // Waveform controls
    document.getElementById('wf-zoom-in').addEventListener('click', () => { waveformZoom = Math.min(waveformZoom * 1.5, 10); drawWaveform(); });
    document.getElementById('wf-zoom-out').addEventListener('click', () => { waveformZoom = Math.max(waveformZoom / 1.5, 1); drawWaveform(); });

    // Nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => navigateTo(item.dataset.page));
    });
});

// ===== API Helper =====
async function api(path, options = {}) {
    const headers = { ...options.headers };
    if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
    if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';

    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

    if (res.status === 401) {
        handleLogout();
        throw new Error('Sessiya tugadi');
    }

    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || `Xatolik: ${res.status}`);
    }

    if (res.status === 204) return null;
    return res.json();
}

// ===== Auth =====
async function handleLogin(e) {
    e.preventDefault();
    const btn = document.getElementById('login-btn');
    const errEl = document.getElementById('login-error');
    btn.disabled = true;
    errEl.classList.add('hidden');

    try {
        const data = await api('/admin/auth/login', {
            method: 'POST',
            body: JSON.stringify({
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
            }),
        });
        authToken = data.access_token;
        localStorage.setItem('admin_token', authToken);
        showDashboard();
        loadDashboardData();
    } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.remove('hidden');
    } finally {
        btn.disabled = false;
    }
}

function handleLogout() {
    authToken = null;
    localStorage.removeItem('admin_token');
    document.getElementById('login-screen').classList.add('active');
    document.getElementById('dashboard-screen').classList.remove('active');
}

function showDashboard() {
    document.getElementById('login-screen').classList.remove('active');
    document.getElementById('dashboard-screen').classList.add('active');
}

// ===== Navigation =====
function navigateTo(page) {
    currentPage = page;
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    document.getElementById(`page-${page}`)?.classList.add('active');
    document.querySelector(`[data-page="${page}"]`)?.classList.add('active');

    const titles = {
        dashboard: 'Dashboard', book: 'Kitob', pages: 'Sahifalar',
        audio: 'Audio', waveform: 'Waveform Editor',
        feedback: 'Fikr-mulohazalar', settings: 'Sozlamalar', audit: 'Audit Log',
    };
    document.getElementById('page-title').textContent = titles[page] || page;

    // Load page data
    const loaders = {
        dashboard: loadDashboardData, book: loadBook, pages: loadPages,
        audio: loadAudioFiles, waveform: loadWaveformSelect,
        feedback: loadFeedback, settings: loadSettings, audit: loadAuditLog,
    };
    loaders[page]?.();

    // Close mobile sidebar
    document.querySelector('.sidebar')?.classList.remove('open');
}

function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}

// ===== Dashboard =====
async function loadDashboardData() {
    try {
        const manifest = await api('/manifest');
        document.getElementById('stat-pages').textContent = manifest.total_pages;
        document.getElementById('stat-units').textContent = manifest.total_units;
        document.getElementById('stat-segments').textContent = manifest.total_segments;
        document.getElementById('stat-version').textContent = `v${manifest.version}`;
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

// ===== Book =====
async function loadBook() {
    try {
        const book = await api('/admin/book');
        document.getElementById('book-info').innerHTML = `
            <div style="display:grid;gap:12px;">
                <p><strong>Nomi:</strong> ${book.title}</p>
                <p><strong>Muallif:</strong> ${book.author || '—'}</p>
                <p><strong>Jami sahifalar:</strong> ${book.total_pages}</p>
                <p><strong>Manifest versiya:</strong> v${book.manifest_version}</p>
                <p><strong>Holat:</strong> ${book.is_published ? '✅ Nashr qilingan' : '⏳ Qoralama'}</p>
            </div>
        `;

        const chaptersHtml = (book.chapters || []).map(ch => `
            <div class="segment-item">
                <span class="segment-idx">${ch.sort_order + 1}</span>
                <span style="flex:1">${ch.title}</span>
                <span class="text-muted">Sahifalar: ${ch.start_page || '?'} — ${ch.end_page || '?'}</span>
                <button class="btn btn-sm btn-danger" onclick="deleteChapter(${ch.id})">🗑️</button>
            </div>
        `).join('') || '<p class="text-muted">Boblar yo\'q</p>';
        document.getElementById('chapters-list').innerHTML = chaptersHtml;
    } catch (err) {
        document.getElementById('book-info').innerHTML = `<p class="text-danger">${err.message}</p>`;
    }
}

// ===== Pages =====
async function loadPages() {
    try {
        const pages = await api('/admin/book/pages');
        const grid = document.getElementById('pages-grid');
        if (!pages.length) {
            grid.innerHTML = '<p class="text-muted">Sahifalar yo\'q. PDF import qiling yoki rasm yuklang.</p>';
            return;
        }

        const statusBadge = (s) => {
            const map = {
                empty: ['⚪', 'Bo\'sh', ''],
                pending: ['⏳', 'Kutilmoqda', 'text-warning'],
                analyzing: ['🔄', 'Tahlil...', 'text-info'],
                draft: ['📝', 'Qoralama', 'text-warning'],
                published: ['✅', 'Nashr', 'text-success'],
                error: ['❌', 'Xatolik', 'text-danger'],
            };
            const [icon, label, cls] = map[s] || map.empty;
            return `<span class="badge ${cls}">${icon} ${label}</span>`;
        };

        grid.innerHTML = pages.map(p => `
            <div class="page-thumb" onclick="openPageAnnotator(${p.id}, ${p.page_number})">
                <img src="${p.image_url || p.source_image_url || ''}" alt="Sahifa ${p.page_number}"
                     onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22160%22 height=%22200%22><rect fill=%22%2321242f%22 width=%22160%22 height=%22200%22/><text x=%2250%%22 y=%2250%%22 fill=%22%236b7280%22 text-anchor=%22middle%22>${p.page_number}</text></svg>'">
                <div class="page-thumb-info">
                    <span class="page-num">Sahifa ${p.page_number}</span>
                    <span class="page-status">${statusBadge(p.analysis_status)} · ${p.unit_count || 0} unit</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        document.getElementById('pages-grid').innerHTML = `<p class="text-danger">${err.message}</p>`;
    }
}

function openPageAnnotator(pageId, pageNumber) {
    window.open(`page-editor.html#page-${pageId}`, '_blank');
}

async function handlePageImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const pageNumber = prompt('Sahifa raqamini kiriting:', '1');
    if (!pageNumber) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('page_number', pageNumber);

    try {
        const result = await api('/admin/book/pages/upload-image', { method: 'POST', body: formData });
        alert(`✅ Rasm yuklandi! Status: ${result.analysis_status}`);
        loadPages();
    } catch (err) {
        alert(`❌ ${err.message}`);
    }
    e.target.value = '';
}

async function createUnit(pageId) {
    try {
        await api(`/admin/book/pages/${pageId}/units`, {
            method: 'POST',
            body: JSON.stringify({
                text_content: document.getElementById('unit-text').value,
                unit_type: document.getElementById('unit-type').value,
                bbox_x: parseFloat(document.getElementById('unit-x').value),
                bbox_y: parseFloat(document.getElementById('unit-y').value),
                bbox_w: parseFloat(document.getElementById('unit-w').value),
                bbox_h: parseFloat(document.getElementById('unit-h').value),
            }),
        });
        closeModal();
        loadPages();
    } catch (err) {
        alert(err.message);
    }
}

// ===== PDF Import =====
function triggerPdfImport() { document.getElementById('pdf-input').click(); }

async function handlePdfUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const result = await api('/admin/book/import-pdf', { method: 'POST', body: formData });
        alert(`PDF import boshlandi! Task ID: ${result.task_id}`);
        setTimeout(() => loadDashboardData(), 3000);
    } catch (err) {
        alert(`Xatolik: ${err.message}`);
    }
    e.target.value = '';
}

// ===== Audio =====
let audioPlayerEl = null;
let currentAudioFiles = [];

function initAudioPlayer() {
    audioPlayerEl = document.getElementById('audio-element');
    if (!audioPlayerEl) return;

    const seekBar = document.getElementById('audio-player-seek');
    const volumeBar = document.getElementById('audio-player-volume');
    const toggleBtn = document.getElementById('audio-player-toggle');
    const closeBtn = document.getElementById('audio-player-close');

    audioPlayerEl.addEventListener('timeupdate', () => {
        if (!audioPlayerEl.duration) return;
        const pct = (audioPlayerEl.currentTime / audioPlayerEl.duration) * 100;
        seekBar.value = pct;
        document.getElementById('audio-player-current').textContent = formatTimeSec(audioPlayerEl.currentTime);
    });

    audioPlayerEl.addEventListener('loadedmetadata', () => {
        document.getElementById('audio-player-duration').textContent = formatTimeSec(audioPlayerEl.duration);
    });

    audioPlayerEl.addEventListener('ended', () => {
        toggleBtn.textContent = '▶️';
    });

    seekBar.addEventListener('input', () => {
        if (audioPlayerEl.duration) {
            audioPlayerEl.currentTime = (seekBar.value / 100) * audioPlayerEl.duration;
        }
    });

    volumeBar.addEventListener('input', () => {
        audioPlayerEl.volume = volumeBar.value / 100;
    });
    audioPlayerEl.volume = 0.8;

    toggleBtn.addEventListener('click', () => {
        if (audioPlayerEl.paused) {
            audioPlayerEl.play();
            toggleBtn.textContent = '⏸️';
        } else {
            audioPlayerEl.pause();
            toggleBtn.textContent = '▶️';
        }
    });

    closeBtn.addEventListener('click', () => {
        audioPlayerEl.pause();
        document.getElementById('audio-player-bar').style.display = 'none';
    });
}

function playAudioFile(url, name) {
    if (!audioPlayerEl) initAudioPlayer();
    const bar = document.getElementById('audio-player-bar');
    bar.style.display = 'block';
    document.getElementById('audio-player-name').textContent = name || 'Audio';
    document.getElementById('audio-player-toggle').textContent = '⏸️';
    audioPlayerEl.src = url;
    audioPlayerEl.play().catch(() => { });
}

function playSegmentRange(url, startMs, endMs, name) {
    if (!audioPlayerEl) initAudioPlayer();
    const bar = document.getElementById('audio-player-bar');
    bar.style.display = 'block';
    document.getElementById('audio-player-name').textContent = name || 'Segment';
    document.getElementById('audio-player-toggle').textContent = '⏸️';
    audioPlayerEl.src = url;
    audioPlayerEl.currentTime = startMs / 1000;
    audioPlayerEl.play().catch(() => { });

    // Stop at endMs
    const checkEnd = () => {
        if (audioPlayerEl.currentTime >= endMs / 1000) {
            audioPlayerEl.pause();
            document.getElementById('audio-player-toggle').textContent = '▶️';
            audioPlayerEl.removeEventListener('timeupdate', checkEnd);
        }
    };
    audioPlayerEl.addEventListener('timeupdate', checkEnd);
}

function formatTimeSec(sec) {
    if (!sec || isNaN(sec)) return '0:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${String(s).padStart(2, '0')}`;
}

async function loadAudioFiles() {
    initAudioPlayer();
    try {
        const files = await api('/admin/audio/files');
        currentAudioFiles = files;
        const container = document.getElementById('audio-files-container');
        const statsRow = document.getElementById('audio-stats-row');

        // Stats
        const total = files.length;
        const ready = files.filter(f => f.status === 'ready').length;
        const segmented = files.filter(f => f.status === 'segmented').length;
        const totalSegs = files.reduce((sum, f) => sum + (f.segment_count || 0), 0);

        statsRow.innerHTML = `
            <div class="audio-stat-chip"><strong>${total}</strong> audio fayl</div>
            <div class="audio-stat-chip text-success"><strong>${ready}</strong> tayyor</div>
            <div class="audio-stat-chip"><strong>${segmented}</strong> segmentlangan</div>
            <div class="audio-stat-chip"><strong>${totalSegs}</strong> jami segment</div>
        `;

        if (!files.length) {
            container.innerHTML = `
                <div class="card mt-4">
                    <div class="card-body" style="text-align:center;padding:40px;">
                        <div style="font-size:48px;margin-bottom:16px;opacity:0.5;">🎵</div>
                        <h3 style="color:var(--text-secondary);margin-bottom:8px;">Audio fayllar yo'q</h3>
                        <p class="text-muted">Audio yuklash tugmasini bosing yoki seed_audio.py ni ishga tushiring</p>
                    </div>
                </div>`;
            return;
        }

        container.innerHTML = files.map((f, i) => {
            const statusInfo = getAudioStatusInfo(f.status);
            const duration = f.duration_ms ? formatTime(f.duration_ms) : '—';
            const size = f.file_size_bytes ? `${(f.file_size_bytes / 1024 / 1024).toFixed(1)} MB` : '—';
            const pages = f.page_start ? `Sahifalar: ${f.page_start}${f.page_end && f.page_end !== f.page_start ? '–' + f.page_end : ''}` : '';

            return `
            <div class="audio-file-card" id="audio-card-${f.id}">
                <div class="audio-file-header" onclick="toggleAudioCard(${f.id})">
                    <div class="audio-file-play">
                        <button class="btn btn-sm btn-primary audio-play-mini" onclick="event.stopPropagation(); playAudioById(${f.id})" title="Tinglash">▶️</button>
                    </div>
                    <div class="audio-file-info">
                        <div class="audio-file-name">${escapeHtml(f.original_filename)}</div>
                        <div class="audio-file-meta">
                            <span>${duration}</span>
                            <span>·</span>
                            <span>${size}</span>
                            ${pages ? `<span>· ${pages}</span>` : ''}
                            <span>· ${f.segment_count || 0} segment</span>
                        </div>
                    </div>
                    <div class="audio-status-badge ${statusInfo.cls}">${statusInfo.icon} ${statusInfo.label}</div>
                    <span class="audio-expand-icon" id="expand-${f.id}">▼</span>
                </div>
                <div class="audio-file-body" id="audio-body-${f.id}" style="display:none;">
                    <div class="audio-actions-bar">
                        <button class="btn btn-sm btn-accent" onclick="syncProcessAudio(${f.id})" id="btn-process-${f.id}">
                            🔄 Qayta ishlash
                        </button>
                        <button class="btn btn-sm btn-success" onclick="syncCutSegments(${f.id})" id="btn-cut-${f.id}"
                            ${f.status !== 'segmented' && f.status !== 'ready' ? 'disabled' : ''}>
                            ✂️ Segmentlarni kesish
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteAudioFile(${f.id})">
                            🗑️ O'chirish
                        </button>
                    </div>
                    <div class="audio-progress-area" id="progress-${f.id}" style="display:none;">
                        <div class="progress-bar"><div class="progress-fill" id="progress-fill-${f.id}"></div></div>
                        <span class="text-muted" id="progress-text-${f.id}" style="font-size:12px;margin-top:4px;"></span>
                    </div>
                    ${f.error_message ? `<div class="audio-error-msg">❌ ${escapeHtml(f.error_message)}</div>` : ''}
                    <div class="audio-segments-area" id="segments-area-${f.id}">
                        <p class="text-muted" style="font-size:13px;">Segmentlarni ko'rish uchun kuting...</p>
                    </div>
                </div>
            </div>`;
        }).join('');

    } catch (err) {
        document.getElementById('audio-files-container').innerHTML = `<div class="card mt-4"><div class="card-body"><p class="text-danger">${err.message}</p></div></div>`;
    }
}

function getAudioStatusInfo(status) {
    const map = {
        uploaded: { icon: '📤', label: 'Yuklangan', cls: 'status-uploaded' },
        processing: { icon: '⏳', label: 'Ishlanmoqda', cls: 'status-processing' },
        segmented: { icon: '📊', label: 'Segmentlangan', cls: 'status-segmented' },
        ready: { icon: '✅', label: 'Tayyor', cls: 'status-ready' },
        error: { icon: '❌', label: 'Xatolik', cls: 'status-error' },
    };
    return map[status] || { icon: '❓', label: status, cls: '' };
}

function toggleAudioCard(id) {
    const body = document.getElementById(`audio-body-${id}`);
    const icon = document.getElementById(`expand-${id}`);
    if (body.style.display === 'none') {
        body.style.display = 'block';
        icon.textContent = '▲';
        loadSegmentsInline(id);
    } else {
        body.style.display = 'none';
        icon.textContent = '▼';
    }
}

async function playAudioById(id) {
    try {
        const data = await api(`/admin/audio/files/${id}/play`);
        playAudioFile(data.url, data.filename);
    } catch (err) {
        alert(`Xatolik: ${err.message}`);
    }
}

async function loadSegmentsInline(audioFileId) {
    const area = document.getElementById(`segments-area-${audioFileId}`);
    try {
        const segments = await api(`/admin/audio/files/${audioFileId}/segments`);
        if (!segments.length) {
            area.innerHTML = '<p class="text-muted" style="font-size:13px;padding:8px 0;">Segmentlar yo\'q. "Qayta ishlash" tugmasini bosing.</p>';
            return;
        }

        const audioFile = currentAudioFiles.find(f => f.id === audioFileId);
        const sourceUrl = audioFile ? `/media/${audioFile.original_filename.replace(/ /g, '_').toLowerCase()}` : null;

        area.innerHTML = `
            <div class="segments-header">
                <span style="font-size:13px;font-weight:600;">Segmentlar (${segments.length})</span>
            </div>
            <div class="segments-list-compact">
                ${segments.map(s => {
            const dur = s.duration_ms > 0 ? formatTime(s.duration_ms) : '0:00';
            const canPlay = s.file_url || !s.is_silence;
            return `
                    <div class="segment-chip ${s.is_silence ? 'silence' : 'content'}">
                        <span class="seg-idx">#${s.segment_index}</span>
                        <span class="seg-type">${s.is_silence ? '🔇' : '🔊'}</span>
                        <span class="seg-range">${formatTime(s.start_ms)} → ${formatTime(s.end_ms)}</span>
                        <span class="seg-dur">${dur}</span>
                        ${s.label ? `<span class="seg-label">${escapeHtml(s.label)}</span>` : ''}
                        ${s.file_url ? `<button class="btn btn-sm" onclick="playAudioFile('${s.file_url}', 'Segment #${s.segment_index}')" title="Tinglash">▶️</button>` : ''}
                    </div>`;
        }).join('')}
            </div>
        `;
    } catch (err) {
        area.innerHTML = `<p class="text-danger">${err.message}</p>`;
    }
}

async function syncProcessAudio(id) {
    const btn = document.getElementById(`btn-process-${id}`);
    const progressArea = document.getElementById(`progress-${id}`);
    const progressFill = document.getElementById(`progress-fill-${id}`);
    const progressText = document.getElementById(`progress-text-${id}`);

    btn.disabled = true;
    btn.textContent = '⏳ Ishlanmoqda...';
    progressArea.style.display = 'block';
    progressFill.style.width = '30%';
    progressText.textContent = 'Audio tahlil qilinmoqda...';

    try {
        progressFill.style.width = '50%';
        progressText.textContent = 'FFmpeg: davomiylik, waveform, segmentatsiya...';

        const result = await api(`/admin/audio/files/${id}/sync-process`, { method: 'POST' });

        progressFill.style.width = '100%';
        progressText.textContent = `✅ ${result.message}`;
        progressFill.style.background = 'var(--success)';

        setTimeout(() => {
            progressArea.style.display = 'none';
            progressFill.style.background = '';
            loadAudioFiles();
        }, 2000);
    } catch (err) {
        progressFill.style.width = '100%';
        progressFill.style.background = 'var(--danger)';
        progressText.textContent = `❌ ${err.message}`;
        btn.disabled = false;
        btn.textContent = '🔄 Qayta ishlash';
    }
}

async function syncCutSegments(id) {
    const btn = document.getElementById(`btn-cut-${id}`);
    const progressArea = document.getElementById(`progress-${id}`);
    const progressFill = document.getElementById(`progress-fill-${id}`);
    const progressText = document.getElementById(`progress-text-${id}`);

    btn.disabled = true;
    btn.textContent = '⏳ Kesilmoqda...';
    progressArea.style.display = 'block';
    progressFill.style.width = '40%';
    progressFill.style.background = '';
    progressText.textContent = 'FFmpeg bilan segmentlar kesilmoqda...';

    try {
        const result = await api(`/admin/audio/files/${id}/sync-cut`, { method: 'POST' });

        progressFill.style.width = '100%';
        progressFill.style.background = 'var(--success)';
        progressText.textContent = `✅ ${result.message}`;

        setTimeout(() => {
            progressArea.style.display = 'none';
            progressFill.style.background = '';
            loadAudioFiles();
        }, 2000);
    } catch (err) {
        progressFill.style.width = '100%';
        progressFill.style.background = 'var(--danger)';
        progressText.textContent = `❌ ${err.message}`;
        btn.disabled = false;
        btn.textContent = '✂️ Segmentlarni kesish';
    }
}

async function deleteAudioFile(id) {
    if (!confirm("Bu audio faylni o'chirishni tasdiqlaysizmi? Barcha segmentlar ham o'chiriladi.")) return;
    try {
        await api(`/admin/audio/files/${id}`, { method: 'DELETE' });
        loadAudioFiles();
    } catch (err) {
        alert(`Xatolik: ${err.message}`);
    }
}

async function handleAudioUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('book_id', '1');

    try {
        await api('/admin/audio/upload', { method: 'POST', body: formData });
        alert('Audio yuklandi!');
        loadAudioFiles();
    } catch (err) {
        alert(`Xatolik: ${err.message}`);
    }
    e.target.value = '';
}

async function viewSegments(audioFileId) {
    toggleAudioCard(audioFileId);
}

async function cutSegments(audioFileId) {
    syncCutSegments(audioFileId);
}

// ===== Waveform Editor =====
let currentWaveformPeaks = [];

async function loadWaveformSelect() {
    try {
        const files = await api('/admin/audio/files');
        const select = document.getElementById('waveform-audio-select');
        select.innerHTML = '<option value="">Audio tanlang...</option>' +
            files.map(f => `<option value="${f.id}" data-peaks='${JSON.stringify(f.waveform_peaks || [])}'>${f.original_filename} (${f.status})</option>`).join('');
        select.onchange = () => {
            const opt = select.options[select.selectedIndex];
            currentWaveformPeaks = JSON.parse(opt.dataset?.peaks || '[]');
            drawWaveform();
            if (select.value) loadWaveformSegments(select.value);
        };
    } catch (err) {
        console.error(err);
    }
}

function drawWaveform() {
    const canvas = document.getElementById('waveform-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = Math.max(1200, currentWaveformPeaks.length * waveformZoom);
    canvas.height = 200;

    const w = canvas.width;
    const h = canvas.height;
    const mid = h / 2;

    ctx.fillStyle = '#1a1d27';
    ctx.fillRect(0, 0, w, h);

    if (!currentWaveformPeaks.length) {
        ctx.fillStyle = '#6b7280';
        ctx.font = '14px Inter';
        ctx.textAlign = 'center';
        ctx.fillText('Audio tanlang', w / 2, mid);
        return;
    }

    const barWidth = w / currentWaveformPeaks.length;
    const gradient = ctx.createLinearGradient(0, 0, 0, h);
    gradient.addColorStop(0, '#7c5cfc');
    gradient.addColorStop(0.5, '#c084fc');
    gradient.addColorStop(1, '#7c5cfc');

    ctx.fillStyle = gradient;
    currentWaveformPeaks.forEach((peak, i) => {
        const barH = peak * (h - 20);
        const x = i * barWidth;
        ctx.fillRect(x, mid - barH / 2, Math.max(barWidth - 1, 1), barH);
    });

    // Grid lines
    ctx.strokeStyle = '#2d3140';
    ctx.lineWidth = 1;
    for (let i = 0; i < 10; i++) {
        const x = (w / 10) * i;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
    }
}

async function loadWaveformSegments(audioFileId) {
    try {
        const segments = await api(`/admin/audio/files/${audioFileId}/segments`);
        const container = document.getElementById('segments-preview');
        container.innerHTML = segments.map(s => `
            <div class="segment-item ${s.is_silence ? 'silence' : ''}">
                <span class="segment-idx">#${s.segment_index}</span>
                <span class="segment-time">${formatTime(s.start_ms)} → ${formatTime(s.end_ms)}</span>
                <span>${s.duration_ms}ms</span>
                <span>${s.is_silence ? '🔇 Jimlik' : '🔊 Kontent'}</span>
                <span>${s.label || ''}</span>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

function updateSpeed() {
    const val = document.getElementById('playback-speed').value;
    document.getElementById('speed-label').textContent = `${val}x`;
}

// ===== Publish =====
async function handlePublish() {
    if (!confirm('Kitobni nashr qilishni tasdiqlaysizmi? Bu manifest versiyasini oshiradi.')) return;
    try {
        const result = await api('/admin/book/publish', { method: 'PUT' });
        alert(`✅ ${result.message} (v${result.version})`);
        loadDashboardData();
    } catch (err) {
        alert(`❌ ${err.message}`);
    }
}

// ===== Feedback =====
async function loadFeedback() {
    try {
        const type = document.getElementById('feedback-filter').value;
        const query = type ? `?feedback_type=${type}` : '';
        const items = await api(`/admin/feedback${query}`);
        const tbody = document.getElementById('feedback-tbody');
        tbody.innerHTML = items.map((f, i) => `<tr>
            <td>${i + 1}</td>
            <td>${escapeHtml(f.name)}</td>
            <td>${escapeHtml(f.phone)}</td>
            <td><span class="badge">${f.feedback_type === 'taklif' ? '📝 Taklif' : '🐛 Xatolik'}</span></td>
            <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis">${escapeHtml(f.details)}</td>
            <td>${f.telegram_sent ? '✅' : '❌'}</td>
            <td>${new Date(f.created_at).toLocaleString('uz')}</td>
        </tr>`).join('') || '<tr><td colspan="7" class="text-muted">Ma\'lumot yo\'q</td></tr>';
    } catch (err) {
        document.getElementById('feedback-tbody').innerHTML = `<tr><td colspan="7" class="text-danger">${err.message}</td></tr>`;
    }
}

// ===== Settings =====
async function loadSettings() {
    try {
        const settings = await api('/admin/settings');
        const token = settings.find(s => s.key === 'telegram_bot_token');
        const ids = settings.find(s => s.key === 'telegram_chat_ids');
        document.getElementById('tg-bot-token').value = token?.value || '';
        document.getElementById('tg-chat-ids').value = ids?.value || '';
    } catch (err) {
        console.error(err);
    }
}

async function handleSaveTelegram(e) {
    e.preventDefault();
    try {
        await api('/admin/telegram-settings', {
            method: 'PUT',
            body: JSON.stringify({
                bot_token: document.getElementById('tg-bot-token').value,
                chat_ids: document.getElementById('tg-chat-ids').value,
            }),
        });
        showResult('telegram-result', true, 'Sozlamalar saqlandi!');
    } catch (err) {
        showResult('telegram-result', false, err.message);
    }
}

async function handleTestTelegram() {
    try {
        const result = await api('/admin/telegram-test', { method: 'POST' });
        showResult('telegram-result', result.success, result.message);
    } catch (err) {
        showResult('telegram-result', false, err.message);
    }
}

// ===== Audit Log =====
async function loadAuditLog() {
    try {
        const items = await api('/admin/audit-log');
        const tbody = document.getElementById('audit-tbody');
        tbody.innerHTML = items.map((a, i) => `<tr>
            <td>${i + 1}</td>
            <td>${escapeHtml(a.action)}</td>
            <td>${a.entity_type || '—'}</td>
            <td>${a.entity_id || '—'}</td>
            <td style="max-width:200px;overflow:hidden">${a.details ? JSON.stringify(a.details) : '—'}</td>
            <td>${new Date(a.created_at).toLocaleString('uz')}</td>
        </tr>`).join('') || '<tr><td colspan="6" class="text-muted">Ma\'lumot yo\'q</td></tr>';
    } catch (err) {
        document.getElementById('audit-tbody').innerHTML = `<tr><td colspan="6" class="text-danger">${err.message}</td></tr>`;
    }
}

// ===== Chapters =====
async function deleteChapter(id) {
    if (!confirm("Bu bobni o'chirishni tasdiqlaysizmi?")) return;
    try {
        await api(`/admin/book/chapters/${id}`, { method: 'DELETE' });
        loadBook();
    } catch (err) {
        alert(err.message);
    }
}

// ===== Modal =====
function showModal(title, body, footer = '') {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = body;
    document.getElementById('modal-footer').innerHTML = footer;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ===== Helpers =====
function formatTime(ms) {
    const s = Math.floor(ms / 1000);
    const m = Math.floor(s / 60);
    const secs = s % 60;
    const millis = ms % 1000;
    return `${m}:${String(secs).padStart(2, '0')}.${String(millis).padStart(3, '0')}`;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}

function showResult(elId, success, message) {
    const el = document.getElementById(elId);
    el.classList.remove('hidden');
    el.className = `mt-2 ${success ? 'text-success' : 'text-danger'}`;
    el.textContent = message;
    setTimeout(() => el.classList.add('hidden'), 5000);
}

// Close modal on overlay click
document.addEventListener('click', (e) => {
    if (e.target.id === 'modal-overlay') closeModal();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});
