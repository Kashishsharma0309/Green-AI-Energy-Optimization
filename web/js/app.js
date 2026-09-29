/**
 * NEXUS Master Client Application
 * Handles API orchestration, Chart.js visualizations, view routing,
 * What-If scenario simulations, and Data Studio file ingestion.
 */

class NexusApp {
  constructor() {
    this.currentView = 'simulatorView';
    this.charts = {};
    this.init();
  }

  async init() {
    this.bindNavigation();
    this.bindWhatIfSandbox();
    this.bindUploader();
    await this.loadAllViews();
  }

  bindNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const targetView = item.getAttribute('data-view');
        this.switchView(targetView);
      });
    });
  }

  switchView(viewId) {
    if (!viewId) return;

    // Update nav links
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.getAttribute('data-view') === viewId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Switch view DOM
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.remove('active');
    });

    const activeSec = document.getElementById(viewId);
    if (activeSec) {
      activeSec.classList.add('active');
      this.currentView = viewId;
      this.onViewActivated(viewId);
    }
  }

  onViewActivated(viewId) {
    if (viewId === 'commandView') {
      this.renderCommandCenter();
    } else if (viewId === 'forecastView') {
      this.renderForecastEngine();
    } else if (viewId === 'anomalyView') {
      this.renderAnomalyMatrix();
    } else if (viewId === 'recommendView') {
      this.renderRecommendations();
    } else if (viewId === 'buildingView') {
      this.renderBuildingIntelligence();
    } else if (viewId === 'reportsView') {
      this.renderMonthlyReports();
    }
  }

  async loadAllViews() {
    try {
      await Promise.all([
        this.fetchOverview(),
        this.fetchLiveStream(),
        this.fetchPredictions(),
        this.fetchAnomalies(),
        this.fetchRecommendations(),
        this.fetchMonthlyReports()
      ]);
    } catch (err) {
      console.error("Initial data load notice:", err);
    }
  }

  // --- API DATA FETCHERS & RENDERERS ---

  async fetchOverview() {
    try {
      const res = await fetch('/api/overview');
      const data = await res.json();
      if (!data.success) return;

      const m = data.metrics;
      document.getElementById('kpiTotalKwh').innerText = `${m.total_energy_kwh.toLocaleString()} kWh`;
      document.getElementById('kpiTotalCost').innerText = `₹${m.total_cost_inr.toLocaleString()}`;
      document.getElementById('kpiTotalCo2').innerText = `${m.total_co2_kg.toLocaleString()} kg`;
      document.getElementById('kpiAvgPower').innerText = `${m.avg_power_kw} kW`;

      this.overviewData = data;
    } catch (e) {
      console.warn("Overview fetch:", e);
    }
  }

  async fetchLiveStream() {
    try {
      const res = await fetch('/api/live-stream');
      const data = await res.json();
      if (!data.success) return;
      this.liveStreamData = data;
    } catch (e) {
      console.warn("Live stream fetch:", e);
    }
  }

  async renderCommandCenter() {
    if (!this.liveStreamData || !this.overviewData) {
      await Promise.all([this.fetchOverview(), this.fetchLiveStream()]);
    }

    const series = this.liveStreamData.series || [];
    const labels = series.map(s => s.timestamp_str.slice(5)); // MM-DD HH:mm
    const energyVals = series.map(s => s.energy_kwh);
    const powerVals = series.map(s => s.power_kw);
    const tempVals = series.map(s => s.temperature_c);

    // 1. Live Telemetry Line Chart
    this.createOrUpdateChart('telemetryChart', {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Energy (kWh)',
            data: energyVals,
            borderColor: '#00e5a3',
            backgroundColor: 'rgba(0, 229, 163, 0.08)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0
          },
          {
            label: 'Power Draw (kW)',
            data: powerVals,
            borderColor: '#00c6ff',
            backgroundColor: 'transparent',
            tension: 0.35,
            borderWidth: 1.5,
            pointRadius: 0,
            borderDash: [4, 4]
          }
        ]
      },
      options: this.getCommonChartOptions('Time', 'Units (kWh / kW)')
    });

    // 2. Appliance Consumption Donut
    const apps = this.overviewData.appliances || [];
    this.createOrUpdateChart('applianceDonutChart', {
      type: 'doughnut',
      data: {
        labels: apps.map(a => a.appliance),
        datasets: [{
          data: apps.map(a => a.total_kwh),
          backgroundColor: ['#00e5a3', '#00c6ff', '#fbc531', '#ff5252', '#9b59b6', '#3867d6'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#8ca3b8', font: { family: 'Plus Jakarta Sans', size: 11 } } }
        },
        cutout: '72%'
      }
    });

    // 3. Daily Trend Bar Chart
    const daily = this.overviewData.daily_trend || [];
    this.createOrUpdateChart('dailyTrendChart', {
      type: 'bar',
      data: {
        labels: daily.map(d => d.date.slice(5)),
        datasets: [{
          label: 'Daily Consumption (kWh)',
          data: daily.map(d => d.total_kwh),
          backgroundColor: 'rgba(0, 229, 163, 0.45)',
          borderColor: '#00e5a3',
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: this.getCommonChartOptions('Date', 'Total kWh')
    });
  }

  async fetchPredictions() {
    try {
      const res = await fetch('/api/predict');
      const data = await res.json();
      if (!data.success) return;
      this.predictData = data;
    } catch (e) {
      console.warn("Predictions fetch:", e);
    }
  }

  async renderForecastEngine() {
    if (!this.predictData) await this.fetchPredictions();
    const p = this.predictData;

    // Metrics
    if (p.metrics) {
      document.getElementById('modelR2').innerText = p.metrics.r2;
      document.getElementById('modelMae').innerText = `${p.metrics.mae} kWh`;
      document.getElementById('modelRmse').innerText = `${p.metrics.rmse} kWh`;
    }

    // 48h Forecast Curve
    const fcast = p.forecast_48h || [];
    this.createOrUpdateChart('forecastCurveChart', {
      type: 'line',
      data: {
        labels: fcast.map(f => f.timestamp.slice(11)), // HH:mm
        datasets: [
          {
            label: 'ML Forecast Demand (kWh)',
            data: fcast.map(f => f.forecast_kwh),
            borderColor: '#9b59b6',
            backgroundColor: 'rgba(155, 89, 182, 0.12)',
            fill: true,
            borderWidth: 2.5,
            tension: 0.35,
            pointRadius: 2
          }
        ]
      },
      options: this.getCommonChartOptions('Future Time (Next 48 Hours)', 'Predicted kWh')
    });

    // Feature Importances
    const imps = p.feature_importances || [];
    this.createOrUpdateChart('featureImportanceChart', {
      type: 'bar',
      data: {
        labels: imps.map(i => i.feature),
        datasets: [{
          label: 'Feature Weight',
          data: imps.map(i => i.importance),
          backgroundColor: '#00e5a3',
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(43,76,102,0.2)' }, ticks: { color: '#8ca3b8' } },
          y: { grid: { display: false }, ticks: { color: '#f0f6fc' } }
        }
      }
    });
  }

  bindWhatIfSandbox() {
    const tempSlider = document.getElementById('whatifTemp');
    const occSlider = document.getElementById('whatifOcc');
    const solarSlider = document.getElementById('whatifSolar');

    const updateWhatIf = async () => {
      const tempDelta = parseFloat(tempSlider.value);
      const occPct = parseFloat(occSlider.value);
      const solarCap = parseFloat(solarSlider.value);

      document.getElementById('whatifTempVal').innerText = `+${tempDelta}°C`;
      document.getElementById('whatifOccVal').innerText = `-${occPct}%`;
      document.getElementById('whatifSolarVal').innerText = `${solarCap} kWp`;

      try {
        const res = await fetch('/api/predict/what-if', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            temp_delta_c: tempDelta,
            occupancy_reduction_pct: occPct,
            solar_capacity_kw: solarCap
          })
        });
        const data = await res.json();
        if (!data.success) return;

        // Update Summary Cards
        const s = data.summary;
        document.getElementById('whatifSavingsKwh').innerText = `${s.saved_kwh} kWh`;
        document.getElementById('whatifSavingsCost').innerText = `₹${s.saved_cost_inr.toLocaleString()}`;
        document.getElementById('whatifSavingsPct').innerText = `${s.percentage_savings}%`;

        // Render Sandbox Comparison Curve
        const timeline = data.timeline || [];
        this.createOrUpdateChart('whatifSandboxChart', {
          type: 'line',
          data: {
            labels: timeline.map(t => t.timestamp),
            datasets: [
              {
                label: 'Baseline Grid Load (kWh)',
                data: timeline.map(t => t.baseline_kwh),
                borderColor: '#ff5252',
                borderDash: [5, 5],
                borderWidth: 2,
                pointRadius: 0
              },
              {
                label: 'Optimized Green Demand (kWh)',
                data: timeline.map(t => t.optimized_kwh),
                borderColor: '#00e5a3',
                backgroundColor: 'rgba(0, 229, 163, 0.15)',
                fill: true,
                borderWidth: 2,
                pointRadius: 2
              }
            ]
          },
          options: this.getCommonChartOptions('Hour', 'Energy Draw (kWh)')
        });
      } catch (err) {
        console.warn("What if err:", err);
      }
    };

    if (tempSlider && occSlider && solarSlider) {
      tempSlider.addEventListener('input', updateWhatIf);
      occSlider.addEventListener('input', updateWhatIf);
      solarSlider.addEventListener('input', updateWhatIf);
      // Run once on load
      setTimeout(updateWhatIf, 500);
    }
  }

  async fetchAnomalies() {
    try {
      const res = await fetch('/api/anomalies');
      const data = await res.json();
      if (!data.success) return;
      this.anomalyData = data;
    } catch (e) {
      console.warn("Anomalies fetch:", e);
    }
  }

  async renderAnomalyMatrix() {
    if (!this.anomalyData) await this.fetchAnomalies();
    const a = this.anomalyData;

    // Severity badges
    if (a.counts) {
      document.getElementById('anomCriticalCount').innerText = a.counts.Critical;
      document.getElementById('anomHighCount').innerText = a.counts.High;
      document.getElementById('anomMediumCount').innerText = a.counts.Medium;
      document.getElementById('anomTotalCount').innerText = a.counts.Total;
    }

    // Anomaly Appliance Distribution
    const byApp = a.by_appliance || {};
    this.createOrUpdateChart('anomalyApplianceChart', {
      type: 'bar',
      data: {
        labels: Object.keys(byApp),
        datasets: [{
          label: 'Anomalies Detected',
          data: Object.values(byApp),
          backgroundColor: '#ff5252',
          borderRadius: 4
        }]
      },
      options: this.getCommonChartOptions('Appliance', 'Fault Events')
    });

    // Populate Anomaly Table
    const tableBody = document.getElementById('anomalyTableBody');
    if (tableBody) {
      const rows = a.anomalies || [];
      tableBody.innerHTML = rows.slice(0, 25).map(r => {
        let badgeClass = 'badge-medium';
        if (r.severity === 'Critical') badgeClass = 'badge-critical';
        else if (r.severity === 'High') badgeClass = 'badge-high';

        return `
          <tr>
            <td style="font-family:'DM Mono', monospace; font-size:0.75rem;">${r.timestamp}</td>
            <td><b>${r.building}</b> (${r.floor})</td>
            <td>${r.appliance}</td>
            <td style="font-family:'DM Mono', monospace; font-weight:700;">${r.energy_kwh} kWh</td>
            <td><span class="badge ${badgeClass}">${r.severity}</span></td>
            <td style="font-size:0.8rem; color:var(--text-muted);">${r.root_cause}</td>
          </tr>
        `;
      }).join('');
    }
  }

  async fetchRecommendations() {
    try {
      const res = await fetch('/api/recommendations');
      const data = await res.json();
      if (!data.success) return;
      this.recommendData = data;
    } catch (e) {
      console.warn("Recommendations fetch:", e);
    }
  }

  async renderRecommendations() {
    if (!this.recommendData) await this.fetchRecommendations();
    const recs = this.recommendData.recommendations || [];

    const container = document.getElementById('recommendationsList');
    if (container) {
      container.innerHTML = recs.map(r => {
        let badgeClass = 'badge-high';
        if (r.priority === 'Critical') badgeClass = 'badge-critical';
        else if (r.priority === 'Medium') badgeClass = 'badge-medium';

        return `
          <div class="glass-panel" style="border-left: 4px solid ${r.priority === 'Critical' ? 'var(--accent-red)' : 'var(--accent-emerald)'}; margin-bottom:1.25rem;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
              <div>
                <span class="badge ${badgeClass}" style="margin-bottom:0.4rem;">${r.priority} Priority</span>
                <h3 style="font-size:1.1rem; font-weight:700; color:#fff;">${r.title}</h3>
                <div style="font-size:0.78rem; color:var(--accent-emerald); font-family:'DM Mono', monospace; margin-top:0.2rem;">
                  💰 ${r.impact}
                </div>
              </div>
              <button class="btn btn-secondary" style="font-size:0.78rem; padding:0.4rem 0.85rem;" onclick="window.app.applyRecommendation('${r.id}')">
                Apply Action →
              </button>
            </div>
            <p style="font-size:0.88rem; color:var(--text-muted); line-height:1.55; margin-bottom:0.85rem;">
              ${r.description}
            </p>
            <div style="background:rgba(0,229,163,0.06); padding:0.6rem 0.85rem; border-radius:var(--radius-sm); border:1px dashed rgba(0,229,163,0.25); font-size:0.82rem; color:#e2f9f3;">
              ⚡ <b>Automated System Action:</b> ${r.action}
            </div>
          </div>
        `;
      }).join('');
    }
  }

  applyRecommendation(recId) {
    this.showToast(`Applied optimization action: ${recId}. AI controllers synchronizing setpoints...`, 'success');
  }

  async renderBuildingIntelligence() {
    if (!this.overviewData) await this.fetchOverview();
    const blds = this.overviewData.buildings || [];

    this.createOrUpdateChart('buildingComparisonChart', {
      type: 'bar',
      data: {
        labels: blds.map(b => b.building),
        datasets: [
          {
            label: 'Total Energy (kWh)',
            data: blds.map(b => b.total_kwh),
            backgroundColor: '#00e5a3',
            borderRadius: 4
          },
          {
            label: 'Electricity Cost (₹)',
            data: blds.map(b => b.total_cost),
            backgroundColor: '#00c6ff',
            borderRadius: 4
          }
        ]
      },
      options: this.getCommonChartOptions('Building Facility', 'Metrics')
    });
  }

  async fetchMonthlyReports() {
    try {
      const res = await fetch('/api/reports/monthly');
      const data = await res.json();
      if (!data.success) return;
      this.monthlyData = data;
    } catch (e) {
      console.warn("Monthly reports fetch:", e);
    }
  }

  async renderMonthlyReports() {
    if (!this.monthlyData) await this.fetchMonthlyReports();
    const reports = this.monthlyData.monthly_reports || [];

    const container = document.getElementById('monthlyReportsTable');
    if (container) {
      container.innerHTML = reports.map(r => `
        <tr>
          <td><b>${r.month_name}</b></td>
          <td style="font-family:'DM Mono', monospace;">${r.total_kwh.toLocaleString()} kWh</td>
          <td style="font-family:'DM Mono', monospace; color:var(--accent-emerald); font-weight:700;">₹${r.total_cost_inr.toLocaleString()}</td>
          <td style="font-family:'DM Mono', monospace;">${r.total_co2_kg.toLocaleString()} kg</td>
          <td style="font-family:'DM Mono', monospace;">${r.peak_power_kw} kW</td>
          <td style="font-family:'DM Mono', monospace;">${r.energy_intensity_kwh_per_occ} kWh/person</td>
          <td>
            <button class="btn btn-secondary" style="padding:0.25rem 0.6rem; font-size:0.75rem;" onclick="window.print()">
              📄 Export
            </button>
          </td>
        </tr>
      `).join('');
    }
  }

  // --- CSV / EXCEL DATA UPLOADER ---

  bindUploader() {
    const dropzone = document.getElementById('uploadDropzone');
    const fileInput = document.getElementById('fileInput');

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        this.uploadFile(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        this.uploadFile(e.target.files[0]);
      }
    });
  }

  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', document.getElementById('uploadModeSelect')?.value || 'append');

    this.showToast(`Ingesting ${file.name}... Processing columns and validating math...`, 'success');

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        this.showToast(data.message, 'success');
        document.getElementById('uploadResultStatus').innerHTML = `
          <div style="padding:1rem; border-radius:var(--radius-sm); background:rgba(0,229,163,0.1); border:1px solid var(--accent-emerald);">
            <div style="font-weight:700; color:#fff;">✅ Ingestion Successful</div>
            <div style="font-size:0.85rem; color:var(--text-muted); margin-top:0.3rem;">Added ${data.rows_added} records. Columns verified: ${data.columns_detected.join(', ')}</div>
          </div>
        `;
        // Refresh views
        await this.loadAllViews();
      } else {
        this.showToast(`Upload Error: ${data.message}`, 'error');
      }
    } catch (err) {
      this.showToast(`Upload failed: ${err.message}`, 'error');
    }
  }

  // --- CHART HELPERS ---

  createOrUpdateChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.charts[canvasId]) {
      this.charts[canvasId].destroy();
    }

    this.charts[canvasId] = new Chart(canvas, config);
  }

  getCommonChartOptions(xTitle = '', yTitle = '') {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#8ca3b8', font: { family: 'Plus Jakarta Sans', size: 11 } }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(43, 76, 102, 0.15)' },
          ticks: { color: '#8ca3b8', font: { family: 'DM Mono', size: 10 } },
          title: xTitle ? { display: true, text: xTitle, color: '#5c7489', font: { size: 10 } } : {}
        },
        y: {
          grid: { color: 'rgba(43, 76, 102, 0.2)' },
          ticks: { color: '#8ca3b8', font: { family: 'DM Mono', size: 10 } },
          title: yTitle ? { display: true, text: yTitle, color: '#5c7489', font: { size: 10 } } : {}
        }
      }
    };
  }

  showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${type === 'success' ? '✅' : '❌'}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 4500);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.app = new NexusApp();
});
