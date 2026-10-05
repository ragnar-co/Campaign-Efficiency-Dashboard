// Vanilla JS dashboard controller. All metric values are rendered exactly as
// received from the backend; no ratio is ever recomputed client-side
// (UI_SPEC.md State Management Plan). Only cosmetic derived text (e.g. "X%
// lower than average") is computed here, from already-fetched real numbers —
// never a fabricated/placeholder value.

(() => {
  "use strict";

  let currentDatasetId = null;
  let cpqlChart = null;
  let qualRateChart = null;
  const LAST_DATASET_KEY = "ced:lastDatasetId";

  // Validated categorical palette (dataviz skill reference instance, light
  // mode), assigned in this fixed order to channels as they arrive from the
  // backend (already alphabetically sorted) — never re-ordered by value, so
  // a channel's color never changes when metrics change (color-follows-
  // entity, not rank).
  const CHANNEL_PALETTE = [
    "#2a78d6", // blue
    "#1baf7a", // aqua
    "#eda100", // yellow
    "#008300", // green
    "#4a3aa7", // violet
    "#e34948", // red
    "#e87ba4", // magenta
    "#eb6834", // orange
  ];
  let channelColorMap = {};

  const el = (id) => document.getElementById(id);

  function fmtMoney(value) {
    if (value === null || value === undefined) return "N/A";
    return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " THB";
  }

  function fmtInt(value) {
    return Number(value).toLocaleString();
  }

  function fmtRate(value) {
    if (value === null || value === undefined) return "N/A";
    return (value * 100).toFixed(2) + "%";
  }

  function fmtCost(value) {
    if (value === null || value === undefined) return "N/A";
    return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " THB";
  }

  function clearChildren(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function showSection(id) {
    el(id).hidden = false;
  }

  function colorForChannel(name) {
    return channelColorMap[name] || "#8a93a3";
  }

  async function parseJsonSafely(response) {
    try {
      return await response.json();
    } catch (_err) {
      return null;
    }
  }

  // ---- Upload ----

  // Trusted, author-written icon markup only (never user data) — safe to set via innerHTML.
  const ICON_CHECK_CIRCLE =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/></svg>';
  const ICON_ALERT_CIRCLE =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><circle cx="12" cy="16" r="0.6" fill="currentColor" stroke="none"/></svg>';

  function buildStatusBanner(state, iconMarkup, titleText, detailText) {
    const resultEl = el("validation-result");
    resultEl.hidden = false;
    resultEl.dataset.state = state;
    clearChildren(resultEl);

    const icon = document.createElement("span");
    icon.className = "status-banner__icon";
    icon.setAttribute("aria-hidden", "true");
    icon.innerHTML = iconMarkup;
    resultEl.appendChild(icon);

    const textGroup = document.createElement("div");
    const title = document.createElement("p");
    title.className = "status-banner__title";
    title.textContent = titleText;
    textGroup.appendChild(title);
    if (detailText) {
      const detail = document.createElement("p");
      detail.className = "status-banner__detail";
      detail.textContent = detailText;
      textGroup.appendChild(detail);
    }
    resultEl.appendChild(textGroup);
    return textGroup;
  }

  async function handleFileSelected() {
    const fileInput = el("csv-file");
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    buildStatusBanner("", ICON_CHECK_CIRCLE, "Importing...");

    try {
      const response = await fetch("/api/datasets/import", { method: "POST", body: formData });
      const body = await parseJsonSafely(response);

      if (response.ok) {
        const importedAt = new Date().toLocaleString(undefined, {
          year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
        });
        const resultEl = el("validation-result");
        buildStatusBanner(
          "success",
          ICON_CHECK_CIRCLE,
          `${fileInput.files[0].name} uploaded successfully`,
          `${fmtInt(body.row_count)} row(s) imported • Imported ${importedAt}`
        );
        resultEl.focus();
        await loadDataset(body.dataset_id);
      } else {
        const textGroup = buildStatusBanner(
          "error",
          ICON_ALERT_CIRCLE,
          (body && body.message) || "Import failed."
        );

        if (body && Array.isArray(body.errors) && body.errors.length) {
          const list = document.createElement("ul");
          const shown = body.errors.slice(0, 100);
          for (const err of shown) {
            const li = document.createElement("li");
            li.textContent = `Row ${err.row}, field "${err.field}": ${err.message}`;
            list.appendChild(li);
          }
          if (body.errors.length > shown.length) {
            const li = document.createElement("li");
            li.textContent = `...and ${body.errors.length - shown.length} more error(s).`;
            list.appendChild(li);
          }
          textGroup.appendChild(list);
        }
        el("validation-result").focus();
      }
    } catch (_err) {
      buildStatusBanner("error", ICON_ALERT_CIRCLE, "Network error while importing CSV.");
      el("validation-result").focus();
    } finally {
      fileInput.value = ""; // allow re-selecting the same filename later
    }
  }

  el("csv-file").addEventListener("change", handleFileSelected);

  // ---- Dataset load ----

  async function loadDataset(datasetId) {
    currentDatasetId = datasetId;
    try {
      window.localStorage.setItem(LAST_DATASET_KEY, String(datasetId));
    } catch (_err) {
      // localStorage unavailable (private mode, etc.) — refresh-persistence
      // of the dataset/brief is a nice-to-have, not a core requirement.
    }
    const channels = await loadChannels(datasetId);
    await loadSummary(datasetId, channels);
    await loadCampaigns(datasetId, "");
    showSection("kpi-section");
    showSection("best-channel-section");
    showSection("chart-section");
    showSection("tables-section");
    showSection("brief-section");
    resetBriefSection();
    await loadLatestBrief(datasetId);
  }

  // Restore the last imported dataset (and its saved brief, if any) on page
  // load/refresh, so a previously generated Campaign Review Brief remains
  // reachable without re-uploading the CSV.
  async function restoreLastDatasetIfAny() {
    let storedId = null;
    try {
      storedId = window.localStorage.getItem(LAST_DATASET_KEY);
    } catch (_err) {
      return;
    }
    if (!storedId) return;

    const response = await fetch(`/api/datasets/${storedId}/summary`);
    if (!response.ok) {
      try {
        window.localStorage.removeItem(LAST_DATASET_KEY);
      } catch (_err) {
        /* ignore */
      }
      return; // stale/unknown dataset id; stay on the upload-only view
    }
    await loadDataset(Number(storedId));
  }

  async function loadSummary(datasetId, channels) {
    const response = await fetch(`/api/datasets/${datasetId}/summary`);
    if (!response.ok) return;
    const summary = await response.json();
    renderKpis(summary, channels || []);
  }

  function renderKpis(summary, channels) {
    el("kpi-spend").textContent = fmtMoney(summary.spend_thb);
    el("kpi-leads").textContent = fmtInt(summary.lead_count);
    el("kpi-qualified-leads").textContent = fmtInt(summary.qualified_lead_count);
    el("kpi-cpl").textContent = summary.cpl === null ? "N/A" : fmtMoney(summary.cpl);
    el("kpi-cpql").textContent = summary.cpql === null ? "N/A" : fmtMoney(summary.cpql);
    el("kpi-qualification-rate").textContent = fmtRate(summary.qualification_rate);

    renderBestChannelCallout(summary, channels);
  }

  function renderBestChannelCallout(summary, channels) {
    const titleEl = el("best-channel-title");
    const subtitleEl = el("best-channel-subtitle");

    if (!summary.best_cpql_channel || summary.best_cpql_value === null) {
      titleEl.textContent = "Best Channel: N/A";
      subtitleEl.textContent = "No channel has a qualified lead yet, so no eligible lowest-CPQL channel can be determined.";
      return;
    }

    titleEl.textContent = `Best Channel: ${summary.best_cpql_channel}`;

    // Derived purely from already-fetched real numbers (dataset overall CPQL
    // vs this channel's CPQL) — not an AI-generated or hardcoded claim.
    let comparison = "";
    if (summary.cpql && summary.cpql > 0 && channels.length > 1) {
      const pctLower = ((summary.cpql - summary.best_cpql_value) / summary.cpql) * 100;
      if (pctLower > 0.05) {
        comparison = `, which is ${pctLower.toFixed(0)}% lower than the overall dataset average CPQL (${fmtCost(summary.cpql)})`;
      }
    }
    subtitleEl.textContent = `${summary.best_cpql_channel} has the lowest eligible CPQL at ${fmtCost(summary.best_cpql_value)} per qualified lead${comparison}.`;
  }

  async function loadChannels(datasetId) {
    const response = await fetch(`/api/datasets/${datasetId}/channels`);
    if (!response.ok) return [];
    const body = await response.json();

    channelColorMap = {};
    body.channels.forEach((c, i) => {
      channelColorMap[c.channel] = CHANNEL_PALETTE[i % CHANNEL_PALETTE.length];
    });

    renderChannelTable(body.channels);
    renderCharts(body.channels);
    populateChannelFilter(body.channels);
    return body.channels;
  }

  function renderChannelTable(channels) {
    const tbody = document.querySelector("#channel-table tbody");
    clearChildren(tbody);
    for (const c of channels) {
      const tr = document.createElement("tr");

      const channelTd = document.createElement("td");
      const cell = document.createElement("span");
      cell.className = "channel-cell";
      const dot = document.createElement("span");
      dot.className = "channel-dot";
      dot.style.background = colorForChannel(c.channel);
      const label = document.createElement("span");
      label.textContent = c.channel;
      cell.appendChild(dot);
      cell.appendChild(label);
      channelTd.appendChild(cell);
      tr.appendChild(channelTd);

      const cells = [
        fmtMoney(c.spend_thb),
        fmtInt(c.lead_count),
        fmtInt(c.qualified_lead_count),
        c.cpl === null ? "N/A" : fmtCost(c.cpl),
        c.cpql === null ? "N/A" : fmtCost(c.cpql),
        fmtRate(c.qualification_rate),
      ];
      for (const value of cells) {
        const td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
  }

  let datalabelsRegistered = false;

  function renderCharts(channels) {
    const labels = channels.map((c) => c.channel);
    const colors = channels.map((c) => colorForChannel(c.channel));

    if (typeof Chart === "undefined") return; // CDN unavailable; tables remain the accessible fallback

    if (!datalabelsRegistered && typeof ChartDataLabels !== "undefined") {
      Chart.register(ChartDataLabels);
      datalabelsRegistered = true;
    }
    const hasDatalabels = typeof ChartDataLabels !== "undefined";

    const cpqlData = channels.map((c) => c.cpql);
    const cpqlDatalabels = {
      display: hasDatalabels,
      anchor: "end",
      align: "top",
      color: "#475467",
      font: { size: 11, weight: "600" },
      formatter: (value) => (value === null ? "N/A" : "฿" + value.toLocaleString(undefined, { maximumFractionDigits: 0 })),
    };
    if (cpqlChart) {
      cpqlChart.data.labels = labels;
      cpqlChart.data.datasets[0].data = cpqlData;
      cpqlChart.data.datasets[0].backgroundColor = colors;
      cpqlChart.update();
    } else {
      cpqlChart = new Chart(el("cpql-chart").getContext("2d"), {
        type: "bar",
        data: { labels, datasets: [{ label: "CPQL (THB)", data: cpqlData, backgroundColor: colors, borderRadius: 4, maxBarThickness: 48 }] },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: { padding: { top: 20 } },
          plugins: { legend: { display: false }, datalabels: cpqlDatalabels },
          scales: {
            y: { beginAtZero: true, grid: { color: "#e7eaf0" } },
            x: { grid: { display: false } },
          },
        },
      });
    }

    const qualRateData = channels.map((c) => (c.qualification_rate === null ? null : c.qualification_rate * 100));
    const qualRateDatalabels = {
      display: hasDatalabels,
      anchor: "end",
      align: "top",
      color: "#475467",
      font: { size: 11, weight: "600" },
      formatter: (value) => (value === null ? "N/A" : value.toFixed(1) + "%"),
    };
    if (qualRateChart) {
      qualRateChart.data.labels = labels;
      qualRateChart.data.datasets[0].data = qualRateData;
      qualRateChart.data.datasets[0].backgroundColor = colors;
      qualRateChart.update();
    } else {
      qualRateChart = new Chart(el("qualrate-chart").getContext("2d"), {
        type: "bar",
        data: { labels, datasets: [{ label: "Qualification Rate (%)", data: qualRateData, backgroundColor: colors, borderRadius: 4, maxBarThickness: 48 }] },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: { padding: { top: 20 } },
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: (ctx) => `${ctx.parsed.y.toFixed(2)}%` } },
            datalabels: qualRateDatalabels,
          },
          scales: {
            y: { beginAtZero: true, ticks: { callback: (v) => v + "%" }, grid: { color: "#e7eaf0" } },
            x: { grid: { display: false } },
          },
        },
      });
    }
  }

  function populateChannelFilter(channels) {
    const select = el("channel-filter");
    const previousValue = select.value;
    clearChildren(select);
    const allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = "All Channels";
    select.appendChild(allOption);
    for (const c of channels) {
      const option = document.createElement("option");
      option.value = c.channel;
      option.textContent = c.channel;
      select.appendChild(option);
    }
    select.value = [...select.options].some((o) => o.value === previousValue) ? previousValue : "";
  }

  // Campaign Details is rendered a page at a time, not all rows at once —
  // datasets can have tens of thousands of campaigns. `allCampaigns` holds
  // the full channel-filtered result already fetched from the backend;
  // search/pagination below are purely client-side slicing of that array,
  // never a second network request and never altered/recomputed values.
  const CAMPAIGN_PAGE_SIZE = 25;
  let allCampaigns = [];
  let campaignSearchTerm = "";
  let campaignPage = 1;

  el("channel-filter").addEventListener("change", async (event) => {
    if (currentDatasetId === null) return;
    await loadCampaigns(currentDatasetId, event.target.value);
  });

  el("campaign-search").addEventListener("input", (event) => {
    campaignSearchTerm = event.target.value.trim().toLowerCase();
    campaignPage = 1;
    renderCampaignView();
  });

  el("campaign-prev-page").addEventListener("click", () => {
    if (campaignPage > 1) {
      campaignPage -= 1;
      renderCampaignView();
    }
  });

  el("campaign-next-page").addEventListener("click", () => {
    campaignPage += 1;
    renderCampaignView();
  });

  async function loadCampaigns(datasetId, channel) {
    const url = channel
      ? `/api/datasets/${datasetId}/campaigns?channel=${encodeURIComponent(channel)}`
      : `/api/datasets/${datasetId}/campaigns`;
    const response = await fetch(url);
    if (!response.ok) return;
    const body = await response.json();
    allCampaigns = body.campaigns;
    campaignSearchTerm = "";
    campaignPage = 1;
    el("campaign-search").value = "";
    renderCampaignView();
  }

  function filteredCampaigns() {
    if (!campaignSearchTerm) return allCampaigns;
    return allCampaigns.filter(
      (c) =>
        c.campaign_id.toLowerCase().includes(campaignSearchTerm) ||
        c.campaign_name.toLowerCase().includes(campaignSearchTerm)
    );
  }

  function renderCampaignView() {
    const matches = filteredCampaigns();
    const totalPages = Math.max(1, Math.ceil(matches.length / CAMPAIGN_PAGE_SIZE));
    if (campaignPage > totalPages) campaignPage = totalPages;

    const start = (campaignPage - 1) * CAMPAIGN_PAGE_SIZE;
    const pageItems = matches.slice(start, start + CAMPAIGN_PAGE_SIZE);
    renderCampaignTable(pageItems, matches.length === 0);

    const statusEl = el("campaign-pagination-status");
    if (matches.length === 0) {
      statusEl.textContent = allCampaigns.length === 0 ? "No campaigns for this channel." : "No campaigns match your search.";
    } else {
      const end = Math.min(start + CAMPAIGN_PAGE_SIZE, matches.length);
      const totalLabel = campaignSearchTerm ? `${matches.length} matching campaign(s)` : `${matches.length} campaign(s)`;
      statusEl.textContent = `Showing ${start + 1}-${end} of ${totalLabel}`;
    }

    el("campaign-prev-page").disabled = campaignPage <= 1;
    el("campaign-next-page").disabled = campaignPage >= totalPages || matches.length === 0;
  }

  function renderCampaignTable(campaigns, isEmpty) {
    const tbody = document.querySelector("#campaign-table tbody");
    clearChildren(tbody);
    if (isEmpty) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 9;
      td.textContent = campaignSearchTerm ? "No campaigns match your search." : "No campaigns for this channel.";
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }
    for (const c of campaigns) {
      const tr = document.createElement("tr");
      const cells = [
        c.campaign_id,
        c.campaign_name,
        c.channel,
        fmtMoney(c.spend_thb),
        fmtInt(c.lead_count),
        fmtInt(c.qualified_lead_count),
        c.cpl === null ? "N/A" : fmtCost(c.cpl),
        c.cpql === null ? "N/A" : fmtCost(c.cpql),
        fmtRate(c.qualification_rate),
      ];
      for (const value of cells) {
        const td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
  }

  // ---- AI Brief ----

  function resetBriefSection() {
    const statusEl = el("brief-status");
    statusEl.textContent = "";
    statusEl.dataset.state = "";
    resetBriefList("brief-facts-list");
    resetBriefList("brief-items-list");
    resetBriefList("brief-proposals-list");
  }

  function resetBriefList(listId) {
    const list = el(listId);
    clearChildren(list);
    const li = document.createElement("li");
    li.className = "brief-empty";
    li.textContent = "No brief generated yet.";
    list.appendChild(li);
  }

  async function loadLatestBrief(datasetId) {
    const response = await fetch(`/api/datasets/${datasetId}/briefs/latest`);
    const statusEl = el("brief-status");
    if (response.status === 404) {
      statusEl.textContent = "No brief generated yet for this dataset.";
      statusEl.dataset.state = "";
      return;
    }
    if (!response.ok) {
      const body = await parseJsonSafely(response);
      statusEl.textContent = (body && body.message) || "Unable to load saved brief.";
      statusEl.dataset.state = "error";
      return;
    }
    const brief = await response.json();
    renderBrief(brief);
    statusEl.textContent = `Saved brief from ${brief.generated_at}`;
    statusEl.dataset.state = "";
  }

  el("generate-brief-btn").addEventListener("click", async () => {
    if (currentDatasetId === null) return;
    const button = el("generate-brief-btn");
    const statusEl = el("brief-status");
    button.disabled = true;
    statusEl.dataset.state = "";
    statusEl.textContent = "Generating brief...";
    try {
      const response = await fetch(`/api/datasets/${currentDatasetId}/briefs`, { method: "POST" });
      const body = await parseJsonSafely(response);
      if (response.ok) {
        renderBrief(body);
        statusEl.textContent = `Saved brief from ${body.generated_at}`;
        statusEl.dataset.state = "";
      } else {
        // AI unavailable/misconfigured must not break the rest of the dashboard.
        statusEl.textContent = (body && body.message) || "Brief generation failed.";
        statusEl.dataset.state = "error";
      }
    } catch (_err) {
      statusEl.textContent = "Network error while generating brief.";
      statusEl.dataset.state = "error";
    } finally {
      button.disabled = false;
    }
  });

  function fillBriefList(listId, items) {
    const list = el(listId);
    clearChildren(list);
    if (!items || !items.length) {
      resetBriefList(listId);
      return;
    }
    for (const item of items) {
      const li = document.createElement("li");
      li.textContent = item; // never rendered as HTML — AI output is untrusted text
      list.appendChild(li);
    }
  }

  function renderBrief(brief) {
    fillBriefList("brief-facts-list", brief.facts);
    fillBriefList("brief-items-list", brief.items_to_verify);
    fillBriefList("brief-proposals-list", brief.next_experiment_proposals);
  }

  restoreLastDatasetIfAny();
})();
