(() => {
  const promptEl = document.getElementById('prompt');
  const threadEl = document.getElementById('thread');
  const runBtn = document.getElementById('runBtn');
  const track = document.getElementById('track');
  const trackEmpty = document.getElementById('trackEmpty');
  const trackHint = document.getElementById('trackHint');
  const logEl = document.getElementById('log');
  const logHint = document.getElementById('logHint');
  const reportSection = document.getElementById('reportSection');
  const reportBody = document.getElementById('reportBody');
  const reportSummary = document.getElementById('reportSummary');
  const downloadsEl = document.getElementById('downloads');

  // Friendly labels for known tools; unrecognized tools fall back to their
  // raw name so the console never breaks if the agent's toolset grows.
  const TOOL_LABELS = {
    generate_employee_csv: 'Generate CSV',
    import_csv_to_excel: 'Import → Excel',
    import_csv_to_google_sheets: 'Import → Sheets',
    import_csv_to_ods: 'Import → ODS',
  };

  let stationEls = []; // { tool, el, dotEl, statusEl, readoutEl, resolved }

  function toolLabel(tool) {
    return TOOL_LABELS[tool] || tool.replace(/_/g, ' ');
  }

  function timeNow() {
    const d = new Date();
    return d.toTimeString().slice(0, 8);
  }

  function resetRun() {
    stationEls = [];
    track.querySelectorAll('.station').forEach((el) => el.remove());
    trackEmpty.style.display = '';
    trackHint.textContent = 'planning…';
    logEl.innerHTML = '';
    logHint.textContent = 'running';
    reportSection.classList.add('is-hidden');
    reportBody.innerHTML = '';
    downloadsEl.innerHTML = '';
    reportSummary.textContent = '';
  }

  function appendLog(kind, tag, body) {
    const line = document.createElement('div');
    line.className = `log-line log-line--${kind}`;
    const tagHtml = tag ? `<span class="log-line__tag">${tag}</span> ` : '';
    line.innerHTML = `<span class="log-line__time">${timeNow()}</span><span class="log-line__body">${tagHtml}${escapeHtml(body)}</span>`;
    logEl.appendChild(line);
    logEl.scrollTop = logEl.scrollHeight;
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function addStation(tool, args) {
    trackEmpty.style.display = 'none';
    trackHint.textContent = `${stationEls.filter(s => !s.resolved).length + 1} station active`;

    const el = document.createElement('div');
    el.className = 'station is-running';
    el.innerHTML = `
      <div class="station__dot"></div>
      <div class="station__label">${escapeHtml(toolLabel(tool))}</div>
      <div class="station__status">running</div>
      <div class="station__readout"></div>
    `;
    track.appendChild(el);

    const entry = {
      tool,
      el,
      statusEl: el.querySelector('.station__status'),
      readoutEl: el.querySelector('.station__readout'),
      resolved: false,
    };
    stationEls.push(entry);

    const argStr = Object.entries(args || {}).map(([k, v]) => `${k}=${JSON.stringify(v)}`).join(', ');
    appendLog('call', 'CALL', `${tool}(${argStr})`);
  }

  function resolveStation(tool, result) {
    const entry = stationEls.find((s) => s.tool === tool && !s.resolved);
    if (!entry) return;

    entry.resolved = true;
    const ok = !!result.success;
    entry.el.classList.remove('is-running');
    entry.el.classList.add(ok ? 'is-success' : 'is-failed');
    entry.statusEl.textContent = ok ? 'success' : 'failed';

    entry.readoutEl.innerHTML = buildReadout(tool, result);

    const remaining = stationEls.filter((s) => !s.resolved).length;
    trackHint.textContent = remaining > 0 ? `${remaining} station active` : 'idle';

    appendLog(ok ? 'ok' : 'fail', ok ? 'OK' : 'FAIL', `${tool} ${ok ? 'succeeded' : `failed: ${result.error || 'unknown error'}`}`);
  }

  function buildReadout(tool, result) {
    if (!result.success) {
      return escapeHtml(result.error || 'unknown error');
    }
    const rows = [];
    if (result.rows != null) rows.push(`rows: ${result.rows}`);
    if (result.method) rows.push(`via: ${result.method}`);
    if (result.filepath) rows.push(`file: ${escapeHtml(result.filepath.split(/[\\/]/).pop())}`);
    if (result.path) rows.push(`file: ${escapeHtml(result.path.split(/[\\/]/).pop())}`);
    if (result.spreadsheet_url) {
      return `<a href="${result.spreadsheet_url}" target="_blank" rel="noopener">open sheet ↗</a>`;
    }
    return rows.length ? rows.map(escapeHtml).join('<br>') : 'done';
  }

  function renderReport(report) {
    reportSection.classList.remove('is-hidden');
    report.steps.forEach((step, i) => {
      const ok = !!step.result.success;
      const details = step.result.error || step.result.filepath || step.result.path || step.result.spreadsheet_url || '';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td class="tool-cell">${escapeHtml(toolLabel(step.tool))}</td>
        <td class="${ok ? 'status--ok' : 'status--fail'}">${ok ? 'success' : 'failed'}</td>
        <td>${escapeHtml(String(details))}</td>
      `;
      reportBody.appendChild(tr);
    });
    reportSummary.textContent = report.summary || 'No summary returned.';

    // Create download links for each file
    report.steps.forEach((step) => {
      const r = step.result;
      if (!r.success) return;
      // CSV / Excel / ODS file
      if (r.filepath) {
        const filename = r.filepath.split(/[\\/]/).pop();
        const a = document.createElement('a');
        a.className = 'download-link';
        a.href = `/api/download?path=${encodeURIComponent(filename)}`;
        a.textContent = `⬇ ${filename}`;
        downloadsEl.appendChild(a);
      } else if (r.path) {
        const filename = r.path.split(/[\\/]/).pop();
        const a = document.createElement('a');
        a.className = 'download-link';
        a.href = `/api/download?path=${encodeURIComponent(filename)}`;
        a.textContent = `⬇ ${filename}`;
        downloadsEl.appendChild(a);
      }
      // Google Sheet
      if (r.spreadsheet_url) {
        const a = document.createElement('a');
        a.className = 'download-link';
        a.href = r.spreadsheet_url;
        a.target = '_blank';
        a.rel = 'noopener';
        a.textContent = '📊 open Google Sheet';
        downloadsEl.appendChild(a);
      }
    });
  }

  async function runAgent() {
    const prompt = promptEl.value.trim();
    if (!prompt) {
      promptEl.focus();
      return;
    }

    resetRun();
    runBtn.disabled = true;
    runBtn.classList.add('is-running');

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, thread_id: threadEl.value.trim() || 'web-session' }),
      });

      if (!res.ok || !res.body) {
        throw new Error(`Server responded ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let idx;
        while ((idx = buffer.indexOf('\n\n')) !== -1) {
          const frame = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);
          handleFrame(frame);
        }
      }
    } catch (err) {
      appendLog('error', 'ERROR', err.message || String(err));
      trackHint.textContent = 'connection error';
    } finally {
      runBtn.disabled = false;
      runBtn.classList.remove('is-running');
      logHint.textContent = 'idle';
    }
  }

  function handleFrame(frame) {
    let event = 'message';
    let dataLine = '';
    frame.split('\n').forEach((line) => {
      if (line.startsWith('event:')) event = line.slice(6).trim();
      if (line.startsWith('data:')) dataLine += line.slice(5).trim();
    });

    let data = {};
    try { data = JSON.parse(dataLine); } catch (_) { /* ignore malformed frame */ }

    switch (event) {
      case 'tool_call':
        addStation(data.tool, data.args);
        break;
      case 'tool_result':
        resolveStation(data.tool, data.result);
        break;
      case 'agent_message':
        appendLog('agent', 'AGENT', data.content);
        break;
      case 'report':
        renderReport(data);
        break;
      case 'error':
        appendLog('error', 'ERROR', data.message || 'unknown error');
        trackHint.textContent = 'error';
        break;
      case 'done':
        if (trackHint.textContent !== 'error') trackHint.textContent = 'finished';
        break;
    }
  }

  runBtn.addEventListener('click', runAgent);
  promptEl.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') runAgent();
  });
})();