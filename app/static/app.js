const state = {
  token: localStorage.getItem("fleet_token") || "",
  me: null,
};

const els = {
  authState: document.getElementById("authState"),
  loginCard: document.getElementById("loginCard"),
  loginForm: document.getElementById("loginForm"),
  loginError: document.getElementById("loginError"),
  statsGrid: document.getElementById("statsGrid"),
  txFormCard: document.getElementById("txFormCard"),
  txTableCard: document.getElementById("txTableCard"),
  alertsCard: document.getElementById("alertsCard"),
  statTransactions: document.getElementById("statTransactions"),
  statGallons: document.getElementById("statGallons"),
  statSpend: document.getElementById("statSpend"),
  statAlerts: document.getElementById("statAlerts"),
  vehicleSelect: document.getElementById("vehicleSelect"),
  driverSelect: document.getElementById("driverSelect"),
  siteSelect: document.getElementById("siteSelect"),
  txForm: document.getElementById("txForm"),
  txResult: document.getElementById("txResult"),
  txBody: document.getElementById("txBody"),
  alertsList: document.getElementById("alertsList"),
};

function headers() {
  return state.token ? { Authorization: `Bearer ${state.token}` } : {};
}

function showSignedOut() {
  els.authState.textContent = "Signed out";
  els.loginCard.classList.remove("hidden");
  els.statsGrid.classList.add("hidden");
  els.txFormCard.classList.add("hidden");
  els.txTableCard.classList.add("hidden");
  els.alertsCard.classList.add("hidden");
}

function showSignedIn() {
  els.loginCard.classList.add("hidden");
  els.statsGrid.classList.remove("hidden");
  els.txFormCard.classList.remove("hidden");
  els.txTableCard.classList.remove("hidden");
  els.alertsCard.classList.remove("hidden");
  els.authState.textContent = `${state.me.full_name} (${state.me.role})`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...headers(),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {
      // noop
    }
    throw new Error(detail);
  }

  return response.json();
}

async function login(email, password) {
  const body = new URLSearchParams();
  body.set("username", email);
  body.set("password", password);

  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!response.ok) {
    throw new Error("Invalid login");
  }

  const data = await response.json();
  state.token = data.access_token;
  localStorage.setItem("fleet_token", state.token);
}

function fillSelect(el, items, getLabel, includeBlank = false) {
  el.innerHTML = "";
  if (includeBlank) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No site";
    el.appendChild(opt);
  }

  for (const item of items) {
    const opt = document.createElement("option");
    opt.value = String(item.id);
    opt.textContent = getLabel(item);
    el.appendChild(opt);
  }
}

async function loadLookups() {
  const [vehicles, drivers, sites] = await Promise.all([
    api("/api/vehicles"),
    api("/api/drivers"),
    api("/api/fuel-sites"),
  ]);

  fillSelect(els.vehicleSelect, vehicles, (v) => `${v.unit_number} (${v.tank_capacity_gallons} gal)`);
  fillSelect(els.driverSelect, drivers, (d) => `${d.name} (${d.license_number})`);
  fillSelect(els.siteSelect, sites, (s) => `${s.name}${s.location ? ` - ${s.location}` : ""}`, true);
}

function renderTransactions(rows) {
  els.txBody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${new Date(row.occurred_at).toLocaleString()}</td>
      <td>${row.vehicle_unit}</td>
      <td>${row.driver_name}</td>
      <td>${row.fuel_site_name || "-"}</td>
      <td>${row.gallons.toFixed(1)}</td>
      <td>$${row.price_per_gallon.toFixed(2)}</td>
      <td>${row.odometer}</td>
    `;
    els.txBody.appendChild(tr);
  }
}

function renderAlerts(alerts) {
  els.alertsList.innerHTML = "";
  if (!alerts.length) {
    const li = document.createElement("li");
    li.textContent = "No anomalies in recent data.";
    els.alertsList.appendChild(li);
    return;
  }

  for (const alert of alerts.slice(0, 20)) {
    const li = document.createElement("li");
    li.textContent = `[${alert.severity}] ${alert.code}: ${alert.message}`;
    els.alertsList.appendChild(li);
  }
}

async function refreshDashboard() {
  const [summary, rows, alerts] = await Promise.all([
    api("/api/dashboard/summary?days=30"),
    api("/api/fuel-transactions?limit=50"),
    api("/api/dashboard/anomalies"),
  ]);

  els.statTransactions.textContent = String(summary.total_transactions);
  els.statGallons.textContent = summary.total_gallons.toFixed(1);
  els.statSpend.textContent = `$${summary.total_spend.toFixed(2)}`;
  els.statAlerts.textContent = String(summary.alerts);

  renderTransactions(rows);
  renderAlerts(alerts);
}

async function bootstrapSignedIn() {
  state.me = await api("/api/auth/me");
  showSignedIn();
  await loadLookups();
  await refreshDashboard();
}

els.loginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  els.loginError.textContent = "";

  const formData = new FormData(els.loginForm);
  const email = String(formData.get("email") || "");
  const password = String(formData.get("password") || "");

  try {
    await login(email, password);
    await bootstrapSignedIn();
  } catch (error) {
    localStorage.removeItem("fleet_token");
    state.token = "";
    showSignedOut();
    els.loginError.textContent = error.message;
  }
});

els.txForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  els.txResult.textContent = "";

  const formData = new FormData(els.txForm);
  const payload = {
    vehicle_id: Number(formData.get("vehicle_id")),
    driver_id: Number(formData.get("driver_id")),
    fuel_site_id: formData.get("fuel_site_id") ? Number(formData.get("fuel_site_id")) : null,
    odometer: Number(formData.get("odometer")),
    gallons: Number(formData.get("gallons")),
    price_per_gallon: Number(formData.get("price_per_gallon")),
    source: String(formData.get("source") || "manual"),
    card_last4: String(formData.get("card_last4") || "").trim() || null,
    notes: String(formData.get("notes") || "").trim() || null,
  };

  try {
    await api("/api/fuel-transactions", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    els.txForm.reset();
    els.txResult.textContent = "Transaction saved.";
    await refreshDashboard();
  } catch (error) {
    els.txResult.textContent = `Error: ${error.message}`;
  }
});

(async function init() {
  if (!state.token) {
    showSignedOut();
    return;
  }

  try {
    await bootstrapSignedIn();
  } catch {
    localStorage.removeItem("fleet_token");
    state.token = "";
    showSignedOut();
  }
})();
