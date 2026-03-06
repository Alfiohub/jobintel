const el = {
  semanticQuery: document.getElementById("semanticQuery"),
  roleFamily: document.getElementById("roleFamily"),
  seniority: document.getElementById("seniority"),
  locationType: document.getElementById("locationType"),
  employmentType: document.getElementById("employmentType"),
  skill: document.getElementById("skill"),
  limit: document.getElementById("limit"),
  searchBtn: document.getElementById("searchBtn"),
  resetBtn: document.getElementById("resetBtn"),
  status: document.getElementById("status"),
  results: document.getElementById("results"),
};

const DB_PATH = "data/jobintel_microsaas.sqlite";
const DEFAULT_PROVIDER = "openai";
const FALLBACK_PROVIDER = "hash";

function setStatus(msg) {
  el.status.textContent = msg;
}

function addOptions(selectEl, values) {
  for (const value of values || []) {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = value;
    selectEl.appendChild(opt);
  }
}

function jobCard(job) {
  const div = document.createElement("div");
  div.className = "job";

  const title = document.createElement("h3");
  const link = document.createElement("a");
  link.href = job.url;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.textContent = `${job.company_name} - ${job.title_clean || job.title_raw}`;
  title.appendChild(link);
  div.appendChild(title);

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = [
    job.normalized_title || "-",
    job.role_family || "-",
    job.seniority || "-",
    job.location_type || "-",
    [job.city, job.country].filter(Boolean).join(", ") || "-",
  ].join(" | ");
  div.appendChild(meta);

  if (job.salary_min || job.salary_max) {
    const salary = document.createElement("div");
    salary.className = "salary";
    const cur = (job.salary_currency || "USD").toUpperCase();
    const min = job.salary_min ? Number(job.salary_min).toLocaleString() : "?";
    const max = job.salary_max ? Number(job.salary_max).toLocaleString() : "?";
    salary.textContent = `${cur} ${min} - ${max}`;
    div.appendChild(salary);
  }

  const tags = document.createElement("div");
  tags.className = "tags";
  if (job.role_family) {
    const t = document.createElement("span");
    t.className = "tag";
    t.textContent = job.role_family;
    tags.appendChild(t);
  }
  for (const s of (job.skills || []).slice(0, 8)) {
    const t = document.createElement("span");
    t.className = "tag";
    t.textContent = s;
    tags.appendChild(t);
  }
  div.appendChild(tags);
  return div;
}

async function api(path, params) {
  const u = new URL(path, window.location.origin);
  for (const [k, v] of Object.entries(params || {})) {
    if (v == null || v === "") continue;
    u.searchParams.set(k, String(v));
  }
  const res = await fetch(u.toString());
  const txt = await res.text();
  const data = txt ? JSON.parse(txt) : null;
  if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);
  return data;
}

async function loadOptions() {
  setStatus("Loading filter options...");
  const data = await api("/v1/indexed/filters/options", {
    db_path: DB_PATH,
  });
  addOptions(el.roleFamily, data.role_family);
  addOptions(el.seniority, data.seniority);
  addOptions(el.locationType, data.location_type);
  addOptions(el.employmentType, data.employment_type);
  addOptions(el.skill, data.skills);
  setStatus("Ready.");
}

async function search() {
  setStatus("Searching...");
  const params = {
    db_path: DB_PATH,
    semantic_query: el.semanticQuery.value.trim(),
    semantic_provider: DEFAULT_PROVIDER,
    role_family: el.roleFamily.value,
    seniority: el.seniority.value,
    location_type: el.locationType.value,
    employment_type: el.employmentType.value,
    skill: el.skill.value,
    limit: el.limit.value || 20,
  };
  let data;
  try {
    data = await api("/v1/indexed/jobs", params);
  } catch (e) {
    // Transparent fallback for user experience.
    data = await api("/v1/indexed/jobs", { ...params, semantic_provider: FALLBACK_PROVIDER });
    setStatus(`Found ${data.length} jobs (fallback mode).`);
  }
  el.results.innerHTML = "";
  if (!data.length) {
    const empty = document.createElement("div");
    empty.className = "nores";
    empty.textContent = "Nessun risultato. Prova a cambiare query o filtri.";
    el.results.appendChild(empty);
  } else {
    for (const row of data) {
      el.results.appendChild(jobCard(row));
    }
    setStatus(`Found ${data.length} jobs.`);
  }
}

function resetForm() {
  el.semanticQuery.value = "";
  el.roleFamily.value = "";
  el.seniority.value = "";
  el.locationType.value = "";
  el.employmentType.value = "";
  el.skill.value = "";
  el.limit.value = 20;
}

el.searchBtn.addEventListener("click", () => {
  search().catch((e) => setStatus(`Error: ${e.message}`));
});
el.resetBtn.addEventListener("click", () => {
  resetForm();
  setStatus("Reset.");
});

loadOptions()
  .then(() => search())
  .catch((e) => setStatus(`Error: ${e.message}`));
