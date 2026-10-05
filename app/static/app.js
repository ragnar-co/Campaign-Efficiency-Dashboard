// Vanilla JS dashboard controller. All metric values are rendered exactly as
// received from the backend; no ratio is ever recomputed client-side
// (UI_SPEC.md State Management Plan).

(() => {
  "use strict";

  let currentDatasetId = null;
  let channelChart = null;

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
    return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function clearChildren(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function showSection(id) {
    el(id).hidden = false;
  }

  async function parseJsonSafely(response) {
    try {
      return await response.json();
    } catch (_err) {
      return null;
    }
  }

  // ---- Upload ----

  el("upload-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const fileInput = el("csv-file");
    const resultEl = el("validation-result");
    if (!fileInput.files.length) return;

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    resultEl.dataset.state = "";
    clearChildren(resultEl);
    resultEl.textContent = "Importing...";

    try {
      const response = await fetch("/api/datasets/import", { method: "POST", body: formData });
      const body = await parseJsonSafely(response);

      if (response.ok) {
        clearChildren(resultEl);
        resultEl.dataset.state = "success";
        resultEl.textContent = `Import succeeded: dataset #${body.dataset_id}, ${fmtInt(body.row_count)} row(s).`;
        resultEl.focus();
        await loadDataset(body.dataset_id);
      } else {
        clearChildren(resultEl);
        resultEl.dataset.state = "error";
        const message = document.createElement("p");
        message.textContent = (body && body.message) || "Import failed.";
        resultEl.appendChild(message);

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
          resultEl.appendChild(list);
        }
        resultEl.focus();
      }
    } catch (_err) {
      clearChildren(resultEl);
      resultEl.dataset.state = "error";
      resultEl.textContent = "Network error while importing CSV.";
      resultEl.focus();
    }
  });

  // ---- Dataset load ----

  async function loadDataset(datasetId) {
    currentDatasetId = datasetId;
    await Promise.all([loadSummary(datasetId), loadChannels(datasetId)]);
    await loadCampaigns(datasetId, "");
    showSection("kpi-section");
    showSection("channel-section");
    showSection("campaign-section");
    showSection("brief-section");
    resetBriefSection();
    await loadLatestBrief(datasetId);
  }

  async function loadSummary(datasetId) {
    const response = await fetch(`/api/datasets/${datasetId}/summary`);
    if (!response.ok) return;
    const summary = await response.json();
    renderKpis(summary);
  }

  function renderKpis(summary) {
    const grid = el("kpi-grid");
    clearChildren(grid);
    const template = el("metric-card-template");
    const cards = [
      ["Spend", fmtMoney(summary.spend_thb)],
      ["Leads", fmtInt(summary.lead_count)],
      ["Qualified Leads", fmtInt(summary.qualified_lead_count)],
      ["CPL (Cost per Lead)", summary.cpl === null ? "N/A" : fmtMoney(summary.cpl)],
      ["CPQL (Cost per Qualified Lead)", summary.cpql === null ? "N/A" : fmtMoney(summary.cpql)],
      ["Qualification Rate", fmtRate(summary.qualification_rate)],
    ];
    for (const [label, value] of cards) {
      const node = template.content.cloneNode(true);
      node.querySelector(".metric-label").textContent = label;
      node.querySelector(".metric-value").textContent = value;
      grid.appendChild(node);
    }

    const callout = el("best-channel-callout");
    if (summary.best_cpql_channel) {
      callout.textContent = `Lowest eligible CPQL channel: ${summary.best_cpql_channel} (${fmtCost(summary.best_cpql_value)} THB per qualified lead)`;
    } else {
      callout.textContent = "Lowest eligible CPQL channel: N/A (no channel has a qualified lead yet)";
    }
  }

  async function loadChannels(datasetId) {
    const response = await fetch(`/api/datasets/${datasetId}/channels`);
    if (!response.ok) return;
    const body = await response.json();
    renderChannelTableAndChart(body.channels);
    populateChannelFilter(body.channels);
  }

  function renderChannelTableAndChart(channels) {
    const tbody = document.querySelector("#channel-table tbody");
    clearChildren(tbody);
    for (const c of channels) {
      const tr = document.createElement("tr");
      const cells = [
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

    const ctx = el("channel-chart").getContext("2d");
    const labels = channels.map((c) => c.channel);
    const data = channels.map((c) => c.cpql);

    if (channelChart) {
      channelChart.data.labels = labels;
      channelChart.data.datasets[0].data = data;
      channelChart.update();
      return;
    }

    if (typeof Chart === "undefined") return; // CDN unavailable; table remains accessible fallback

    channelChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: "CPQL (THB per Qualified Lead)",
            data,
            backgroundColor: "#1d2433",
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  function populateChannelFilter(channels) {
    const select = el("channel-filter");
    const previousValue = select.value;
    clearChildren(select);
    const allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = "All";
    select.appendChild(allOption);
    for (const c of channels) {
      const option = document.createElement("option");
      option.value = c.channel;
      option.textContent = c.channel;
      select.appendChild(option);
    }
    select.value = [...select.options].some((o) => o.value === previousValue) ? previousValue : "";
  }

  el("channel-filter").addEventListener("change", async (event) => {
    if (currentDatasetId === null) return;
    await loadCampaigns(currentDatasetId, event.target.value);
  });

  async function loadCampaigns(datasetId, channel) {
    const url = channel
      ? `/api/datasets/${datasetId}/campaigns?channel=${encodeURIComponent(channel)}`
      : `/api/datasets/${datasetId}/campaigns`;
    const response = await fetch(url);
    if (!response.ok) return;
    const body = await response.json();
    renderCampaignTable(body.campaigns);
  }

  function renderCampaignTable(campaigns) {
    const tbody = document.querySelector("#campaign-table tbody");
    clearChildren(tbody);
    if (!campaigns.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 9;
      td.textContent = "No campaigns for this channel.";
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
    el("brief-status").textContent = "";
    clearChildren(el("brief-view"));
  }

  async function loadLatestBrief(datasetId) {
    const response = await fetch(`/api/datasets/${datasetId}/briefs/latest`);
    if (response.status === 404) {
      el("brief-status").textContent = "No brief generated yet for this dataset.";
      return;
    }
    if (!response.ok) {
      const body = await parseJsonSafely(response);
      el("brief-status").textContent = (body && body.message) || "Unable to load saved brief.";
      return;
    }
    const brief = await response.json();
    renderBrief(brief);
    el("brief-status").textContent = `Saved brief from ${brief.generated_at}`;
  }

  el("generate-brief-btn").addEventListener("click", async () => {
    if (currentDatasetId === null) return;
    const button = el("generate-brief-btn");
    const statusEl = el("brief-status");
    button.disabled = true;
    statusEl.textContent = "Generating brief...";
    try {
      const response = await fetch(`/api/datasets/${currentDatasetId}/briefs`, { method: "POST" });
      const body = await parseJsonSafely(response);
      if (response.ok) {
        renderBrief(body);
        statusEl.textContent = `Saved brief from ${body.generated_at}`;
      } else {
        // AI unavailable/misconfigured must not break the rest of the dashboard.
        statusEl.textContent = (body && body.message) || "Brief generation failed.";
      }
    } catch (_err) {
      statusEl.textContent = "Network error while generating brief.";
    } finally {
      button.disabled = false;
    }
  });

  function renderBrief(brief) {
    const view = el("brief-view");
    clearChildren(view);

    const sections = [
      ["Facts", brief.facts],
      ["Items to Verify", brief.items_to_verify],
      ["Next Experiment Proposals", brief.next_experiment_proposals],
    ];
    for (const [heading, items] of sections) {
      const h3 = document.createElement("h3");
      h3.textContent = heading;
      view.appendChild(h3);
      const ul = document.createElement("ul");
      for (const item of items || []) {
        const li = document.createElement("li");
        li.textContent = item;
        ul.appendChild(li);
      }
      view.appendChild(ul);
    }
  }
})();
