import { api } from './api.js';

// Elements
const el = {
    views: document.querySelectorAll('.view-container'),
    navItems: document.querySelectorAll('.nav-item'),
    pageTitle: document.getElementById('pageTitle'),
    
    // Dashboard
    targetInput: document.getElementById('targetInput'),
    btnStart: document.getElementById('btnStartScan'),
    btnStop: document.getElementById('btnStopScan'),
    chkSubfinder: document.getElementById('tool-subfinder'),
    chkAmass: document.getElementById('tool-amass'),
    chkHttpx: document.getElementById('tool-httpx'),
    
    // Stats
    countTotal: document.getElementById('countTotal'),
    countAlive: document.getElementById('countAlive'),
    scanStatus: document.getElementById('scanStatus'),
    
    // Tables & Logs
    resultsTableBody: document.querySelector('#resultsTable tbody'),
    historyTableBody: document.querySelector('#historyTable tbody'),
    terminal: document.getElementById('terminal'),
    searchTable: document.getElementById('searchTable'),
    btnCopyLogs: document.getElementById('btnCopyLogs'),
    
    toastContainer: document.getElementById('toastContainer'),
    toolHealthContainer: document.getElementById('toolHealthContainer')
};

// State
let currentResults = [];

// Initialization
async function init() {
    logToTerminal('Initializing UI...', 'info');
    setupNavigation();
    setupEventListeners();
    
    try {
        logToTerminal('Waiting for Python bridge...', 'info');
        await api.ensureReady();
        logToTerminal('Connected to Python backend.', 'success');
        
        await checkToolHealth();
        await loadHistory();
        
    } catch (err) {
        showToast('Failed to connect to backend', 'error');
        logToTerminal(err.toString(), 'error');
    }
}

// Navigation
function setupNavigation() {
    el.navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const viewId = item.getAttribute('data-view');
            
            // Update active state
            el.navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            // Show view
            el.views.forEach(v => v.classList.remove('active'));
            document.getElementById(`view-${viewId}`).classList.add('active');
            
            // Update title
            el.pageTitle.textContent = item.textContent.trim();
            
            if(viewId === 'history') {
                loadHistory();
            }
        });
    });
}

// Event Listeners for actions
function setupEventListeners() {
    el.btnStart.addEventListener('click', startScan);
    el.btnStop.addEventListener('click', stopScan);
    
    el.searchTable.addEventListener('input', (e) => {
        renderResultsTable(e.target.value);
    });
    
    if (el.btnCopyLogs) {
        el.btnCopyLogs.addEventListener('click', () => {
            const logs = Array.from(el.terminal.querySelectorAll('.log-line'))
                              .map(line => line.textContent)
                              .join('\n');
                              
            // Fallback to document.execCommand to avoid QtWebEngine Permission API crash
            const textarea = document.createElement('textarea');
            textarea.value = logs;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            try {
                document.execCommand('copy');
                showToast('Logs copied to clipboard');
            } catch (err) {
                showToast('Failed to copy logs', 'error');
            } finally {
                document.body.removeChild(textarea);
            }
        });
    }
    
    // Listen for backend events
    window.addEventListener('log', (e) => {
        logToTerminal(e.detail.message, e.detail.level);
    });
    
    window.addEventListener('progress', (e) => {
        el.scanStatus.textContent = e.detail.message;
    });
    
    window.addEventListener('scan_started', (e) => {
        el.scanStatus.textContent = 'Running...';
        el.scanStatus.style.color = 'var(--accent-primary)';
        currentResults = [];
        renderResultsTable();
    });
    
    window.addEventListener('scan_finished', (e) => {
        el.btnStart.disabled = false;
        el.btnStop.disabled = true;
        
        const data = e.detail;
        if(data.status === 'completed') {
            el.scanStatus.textContent = 'Completed';
            el.scanStatus.style.color = 'var(--accent-primary)';
            currentResults = data.results || [];
            
            el.countTotal.textContent = data.total || 0;
            el.countAlive.textContent = data.alive || 0;
            
            renderResultsTable();
            showToast(`Scan complete: ${data.total} subdomains found.`);
        } else {
            el.scanStatus.textContent = data.status;
            el.scanStatus.style.color = 'var(--accent-danger)';
            showToast(`Scan ${data.status}`, 'error');
        }
    });
}

async function checkToolHealth() {
    const status = await api.checkHealth();
    let html = '<h3>System Status</h3>';
    
    for (const [tool, isInstalled] of Object.entries(status)) {
        html += `
            <div class="health-item">
                <span>${tool.charAt(0).toUpperCase() + tool.slice(1)}</span>
                <span class="status-dot ${isInstalled ? 'ok' : 'error'}" title="${isInstalled ? 'Installed' : 'Not Found'}"></span>
            </div>
        `;
    }
    el.toolHealthContainer.innerHTML = html;
}

async function startScan() {
    const target = el.targetInput.value.trim();
    if (!target) {
        showToast('Please enter a target domain', 'error');
        return;
    }
    
    const config = {
        target: target,
        tools: {
            subfinder: el.chkSubfinder.checked,
            amass: el.chkAmass.checked,
            httpx: el.chkHttpx.checked
        }
    };
    
    el.btnStart.disabled = true;
    el.btnStop.disabled = false;
    el.terminal.innerHTML = '';
    el.countTotal.textContent = '0';
    el.countAlive.textContent = '0';
    
    const started = await api.startScan(config);
    if(!started) {
        showToast('Scan already running', 'error');
        el.btnStart.disabled = false;
        el.btnStop.disabled = true;
    }
}

async function stopScan() {
    el.btnStop.disabled = true;
    await api.stopScan();
}

// Rendering
function renderResultsTable(filter = '') {
    if(currentResults.length === 0) {
        el.resultsTableBody.innerHTML = '<tr class="empty-state"><td colspan="5">No results to display.</td></tr>';
        return;
    }
    
    let html = '';
    const f = filter.toLowerCase();
    
    currentResults.forEach(r => {
        if(f && !r.domain.toLowerCase().includes(f) && !(r.ip || '').includes(f)) {
            return; // Skip if filtered
        }
        
        let sourcesHtml = '';
        if(r.sources) {
            r.sources.forEach(s => {
                sourcesHtml += `<span class="tag ${s}">${s}</span>`;
            });
        }
        
        let statusHtml = '-';
        if(r.is_alive !== null && r.is_alive !== undefined) {
            statusHtml = `<span class="status-tag ${r.is_alive ? 'alive' : 'dead'}">${r.status_code || (r.is_alive ? 'Alive' : 'Dead')}</span>`;
        }
        
        html += `
            <tr>
                <td>${r.domain}</td>
                <td>${sourcesHtml}</td>
                <td>${statusHtml}</td>
                <td>${r.ip || '-'}</td>
                <td><div style="max-width:200px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${r.title || ''}">${r.title || '-'}</div></td>
            </tr>
        `;
    });
    
    if(!html) html = '<tr class="empty-state"><td colspan="5">No results match filter.</td></tr>';
    el.resultsTableBody.innerHTML = html;
}

async function loadHistory() {
    const history = await api.getHistory();
    if(!history || history.length === 0) {
        el.historyTableBody.innerHTML = '<tr class="empty-state"><td colspan="6">No history available.</td></tr>';
        return;
    }
    
    let html = '';
    history.forEach(h => {
        html += `
            <tr>
                <td>${h.target}</td>
                <td>${new Date(h.timestamp).toLocaleString()}</td>
                <td>${JSON.parse(h.tools_used).join(', ')}</td>
                <td>${h.total_domains}</td>
                <td>${h.alive_domains}</td>
                <td><span class="status-tag ${h.status === 'completed' ? 'alive' : 'dead'}">${h.status}</span></td>
            </tr>
        `;
    });
    
    el.historyTableBody.innerHTML = html;
}

function logToTerminal(message, level = 'info') {
    const div = document.createElement('div');
    div.className = `log-line ${level}`;
    const time = new Date().toLocaleTimeString();
    div.textContent = `[${time}] ${message}`;
    el.terminal.appendChild(div);
    el.terminal.scrollTop = el.terminal.scrollHeight;
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    el.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Start
document.addEventListener('DOMContentLoaded', init);
