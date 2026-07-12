const state = {
  userId: 'demo',
  activeFilterId: null,
};

const el = {
  userId: document.getElementById('userId'),
  reloadAllBtn: document.getElementById('reloadAllBtn'),
  filterForm: document.getElementById('filterForm'),
  filterName: document.getElementById('filterName'),
  roleFamily: document.getElementById('roleFamily'),
  seniority: document.getElementById('seniority'),
  locationType: document.getElementById('locationType'),
  country: document.getElementById('country'),
  source: document.getElementById('source'),
  skills: document.getElementById('skills'),
  skillsCustom: document.getElementById('skillsCustom'),
  resetFiltersBtn: document.getElementById('resetFiltersBtn'),
  filtersList: document.getElementById('filtersList'),
  recommendationsList: document.getElementById('recommendationsList'),
  inboxList: document.getElementById('inboxList'),
  refreshMatchesBtn: document.getElementById('refreshMatchesBtn'),
  markSeenBtn: document.getElementById('markSeenBtn'),
  activeFilterInfo: document.getElementById('activeFilterInfo'),
  filterItemTpl: document.getElementById('filterItemTpl'),
  jobItemTpl: document.getElementById('jobItemTpl'),
};

function parseCsv(v) {
  return v.split(',').map((s) => s.trim()).filter(Boolean);
}

function selectedValues(selectEl) {
  return Array.from(selectEl.selectedOptions).map((o) => o.value).filter(Boolean);
}

function unique(values) {
  return Array.from(new Set(values.map((v) => String(v).trim()).filter(Boolean)));
}

function api(path, options = {}) {
  return fetch(path, options).then(async (r) => {
    const text = await r.text();
    const data = text ? JSON.parse(text) : null;
    if (!r.ok) throw new Error(data?.detail || `HTTP ${r.status}`);
    return data;
  });
}

function clearSelect(selectEl) {
  Array.from(selectEl.options).forEach((opt) => {
    opt.selected = false;
  });
}

function enableEasyMultiSelect(selectEl) {
  selectEl.addEventListener('mousedown', (ev) => {
    const target = ev.target;
    if (!(target instanceof HTMLOptionElement)) return;
    ev.preventDefault();
    target.selected = !target.selected;
  });
}

function fillSelect(selectEl, values, defaults = []) {
  selectEl.innerHTML = '';
  values.forEach((value) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    option.selected = defaults.includes(value);
    selectEl.appendChild(option);
  });
}

async function loadFilterOptions() {
  const data = await api('/filters/options');
  fillSelect(el.roleFamily, data.role_family || [], ['data']);
  fillSelect(el.seniority, data.seniority || []);
  fillSelect(el.locationType, data.location_type || [], ['remote']);
  fillSelect(el.country, data.country || [], ['us']);
  fillSelect(el.source, data.source || []);
  fillSelect(el.skills, data.skills || ['python', 'sql'], ['python', 'sql']);
}

async function loadFilters() {
  const data = await api(`/saved-filters?user_id=${encodeURIComponent(state.userId)}`);
  el.filtersList.innerHTML = '';

  for (const f of data) {
    const node = el.filterItemTpl.content.firstElementChild.cloneNode(true);
    node.querySelector('.filter-title').textContent = f.name;
    node.querySelector('.filter-id').textContent = `#${f.id}`;
    node.querySelector('.criteria').textContent = JSON.stringify(f.criteria);

    node.querySelector('[data-action="select"]').onclick = async () => {
      state.activeFilterId = f.id;
      el.activeFilterInfo.textContent = `Active filter #${f.id} - ${f.name}`;
      await Promise.all([loadRecommendations(), loadInbox()]);
      await loadTargets(node.querySelector('.targets'), f.id);
    };

    node.querySelector('[data-action="delete"]').onclick = async () => {
      await api(`/saved-filters/${f.id}`, { method: 'DELETE' });
      if (state.activeFilterId === f.id) {
        state.activeFilterId = null;
        el.activeFilterInfo.textContent = 'Select a filter';
        el.recommendationsList.innerHTML = '';
        el.inboxList.innerHTML = '';
      }
      await loadFilters();
    };

    const webhookInput = node.querySelector('.webhook-input');
    node.querySelector('[data-action="upsert-webhook"]').onclick = async () => {
      const url = webhookInput.value.trim();
      if (!url) return;
      await api(`/notifications/targets/${f.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ webhook_url: url, is_active: true }),
      });
      webhookInput.value = '';
      await loadTargets(node.querySelector('.targets'), f.id);
    };

    await loadTargets(node.querySelector('.targets'), f.id);
    el.filtersList.appendChild(node);
  }
}

async function loadTargets(container, filterId) {
  const targets = await api(`/notifications/targets/${filterId}`);
  container.innerHTML = '';
  for (const t of targets) {
    const row = document.createElement('div');
    row.className = 'actions';
    row.innerHTML = `<span class="hint">${t.webhook_url}</span>`;
    const delBtn = document.createElement('button');
    delBtn.className = 'danger';
    delBtn.textContent = 'Remove';
    delBtn.onclick = async () => {
      await api(`/notifications/targets/${filterId}?webhook_url=${encodeURIComponent(t.webhook_url)}`, { method: 'DELETE' });
      await loadTargets(container, filterId);
    };
    row.appendChild(delBtn);
    container.appendChild(row);
  }
}

async function loadRecommendations() {
  if (!state.activeFilterId) return;
  const rows = await api(`/recommendations/${state.activeFilterId}?limit=20`);
  el.recommendationsList.innerHTML = '';
  rows.forEach((j) => {
    const node = renderJobCard(j, false);
    el.recommendationsList.appendChild(node);
  });
}

async function loadInbox(markSeen = false) {
  if (!state.activeFilterId) return;
  const rows = await api(`/matches/new/${state.activeFilterId}?limit=20${markSeen ? '&mark_seen=true' : ''}`);
  el.inboxList.innerHTML = '';
  rows.forEach((j) => {
    const node = renderJobCard(j, true);
    el.inboxList.appendChild(node);
  });
}

function renderJobCard(job, hasFingerprint) {
  const node = el.jobItemTpl.content.firstElementChild.cloneNode(true);
  const a = node.querySelector('.job-title');
  a.href = job.url;
  a.textContent = `${job.company} - ${job.title}`;
  node.querySelector('.score').textContent = `score ${job.score}`;
  node.querySelector('.meta').textContent = `${job.location || '-'} | ${job.published_at || '-'} | ${job.country || '-'}`;
  node.querySelector('.reasons').textContent = (job.reasons || []).join(', ');

  const actions = ['save', 'dismiss', 'apply'];
  actions.forEach((action) => {
    node.querySelector(`[data-action="${action}"]`).onclick = async () => {
      if (!hasFingerprint || !job.fingerprint) return;
      await api(`/jobs/${job.fingerprint}/actions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: state.userId, action, filter_id: state.activeFilterId, metadata: { from: 'ui' } }),
      });
      await loadInbox();
      await loadRecommendations();
    };
  });

  return node;
}

el.filterForm.onsubmit = async (ev) => {
  ev.preventDefault();
  const payload = {
    user_id: state.userId,
    name: el.filterName.value.trim(),
    criteria: {
      role_family: selectedValues(el.roleFamily),
      seniority: selectedValues(el.seniority),
      location_type: selectedValues(el.locationType),
      country: selectedValues(el.country),
      source: selectedValues(el.source),
      skills: unique([...selectedValues(el.skills), ...parseCsv(el.skillsCustom.value)]),
    },
    is_active: true,
  };
  await api('/saved-filters', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  el.filterName.value = '';
  el.skillsCustom.value = '';
  await loadFilters();
};

el.reloadAllBtn.onclick = async () => {
  state.userId = el.userId.value.trim() || 'demo';
  state.activeFilterId = null;
  el.activeFilterInfo.textContent = 'Select a filter';
  el.recommendationsList.innerHTML = '';
  el.inboxList.innerHTML = '';
  await loadFilters();
};

el.resetFiltersBtn.onclick = () => {
  clearSelect(el.roleFamily);
  clearSelect(el.seniority);
  clearSelect(el.locationType);
  clearSelect(el.country);
  clearSelect(el.source);
  clearSelect(el.skills);
  el.skillsCustom.value = '';
};

el.refreshMatchesBtn.onclick = async () => {
  if (!state.activeFilterId) return;
  await api(`/matches/refresh/${state.activeFilterId}`, { method: 'POST' });
  await Promise.all([loadRecommendations(), loadInbox()]);
};

el.markSeenBtn.onclick = async () => {
  await loadInbox(true);
  await loadInbox(false);
};

(async () => {
  enableEasyMultiSelect(el.roleFamily);
  enableEasyMultiSelect(el.seniority);
  enableEasyMultiSelect(el.locationType);
  enableEasyMultiSelect(el.country);
  enableEasyMultiSelect(el.source);
  enableEasyMultiSelect(el.skills);
  await loadFilterOptions();
  await loadFilters();
})();
