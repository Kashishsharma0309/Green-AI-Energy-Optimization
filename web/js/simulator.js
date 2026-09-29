/**
 * NEXUS Smart Estate & Locality Simulator Engine
 * Provides interactive appliance physics, live thermodynamics, solar balance,
 * and AI Eco-Optimization auto-balancing.
 */

class SmartEstateSimulator {
  constructor() {
    this.timeHour = 14; // 2:00 PM default
    this.outdoorTemp = 33; // 33°C summer day
    this.isSunny = true;
    this.solarCapacityKw = 6.5;
    this.solarActive = true;
    this.batteryStorageKwh = 7.8; // current battery charge
    this.batteryCapacityKwh = 10.0;

    // Appliance state definition
    this.appliances = {
      // 1. Living Room
      living_ac: {
        id: 'living_ac',
        name: 'Dual-Inverter AC (1.5 Ton)',
        room: 'Living Room',
        roomKey: 'living',
        type: 'climate',
        baseWatt: 1600,
        isOn: true,
        setpoint: 19, // Inefficient default to demonstrate AI optimization
        icon: '❄️',
        sliderMin: 16,
        sliderMax: 30,
        sliderUnit: '°C',
        controlType: 'temp'
      },
      living_tv: {
        id: 'living_tv',
        name: '75" 4K OLED Smart TV',
        room: 'Living Room',
        roomKey: 'living',
        type: 'electronics',
        baseWatt: 220,
        isOn: true,
        powerFactor: 1.0,
        icon: '📺',
        controlType: 'switch'
      },
      living_lights: {
        id: 'living_lights',
        name: 'Ambient LED Chandeliers',
        room: 'Living Room',
        roomKey: 'living',
        type: 'lighting',
        baseWatt: 180,
        isOn: true,
        dimmerPct: 100,
        icon: '💡',
        sliderMin: 10,
        sliderMax: 100,
        sliderUnit: '%',
        controlType: 'dimmer'
      },

      // 2. Kitchen
      kitchen_fridge: {
        id: 'kitchen_fridge',
        name: 'Multi-Door Smart Refrigerator',
        room: 'Kitchen',
        roomKey: 'kitchen',
        type: 'cooling',
        baseWatt: 350,
        isOn: true,
        powerFactor: 0.85,
        icon: '🧊',
        controlType: 'switch'
      },
      kitchen_oven: {
        id: 'kitchen_oven',
        name: 'Induction Cooktop & Oven',
        room: 'Kitchen',
        roomKey: 'kitchen',
        type: 'heating',
        baseWatt: 2400,
        isOn: false,
        powerFactor: 0.75,
        icon: '🍳',
        sliderMin: 20,
        sliderMax: 100,
        sliderUnit: '%',
        controlType: 'power'
      },
      kitchen_dishwasher: {
        id: 'kitchen_dishwasher',
        name: 'Smart Eco Dishwasher',
        room: 'Kitchen',
        roomKey: 'kitchen',
        type: 'heavy',
        baseWatt: 1800,
        isOn: true, // Running during afternoon peak
        powerFactor: 1.0,
        icon: '🍽️',
        controlType: 'switch'
      },

      // 3. Master Bedroom
      bed_ac: {
        id: 'bed_ac',
        name: 'Whisper-Quiet Split AC (1.0 Ton)',
        room: 'Master Bedroom',
        roomKey: 'bedroom',
        type: 'climate',
        baseWatt: 1100,
        isOn: true,
        setpoint: 20,
        icon: '❄️',
        sliderMin: 16,
        sliderMax: 30,
        sliderUnit: '°C',
        controlType: 'temp'
      },
      bed_purifier: {
        id: 'bed_purifier',
        name: 'True HEPA Air Purifier',
        room: 'Master Bedroom',
        roomKey: 'bedroom',
        type: 'fan',
        baseWatt: 65,
        isOn: true,
        powerFactor: 1.0,
        icon: '🌀',
        controlType: 'switch'
      },
      bed_lights: {
        id: 'bed_lights',
        name: 'Recessed Smart Ceiling Lights',
        room: 'Master Bedroom',
        roomKey: 'bedroom',
        type: 'lighting',
        baseWatt: 90,
        isOn: true,
        dimmerPct: 80,
        icon: '💡',
        sliderMin: 10,
        sliderMax: 100,
        sliderUnit: '%',
        controlType: 'dimmer'
      },

      // 4. Smart Office
      office_workstation: {
        id: 'office_workstation',
        name: 'Dual-Monitor AI Workstation',
        room: 'Tech Office',
        roomKey: 'office',
        type: 'work',
        baseWatt: 480,
        isOn: true,
        powerFactor: 0.9,
        icon: '🖥️',
        controlType: 'switch'
      },
      office_ac: {
        id: 'office_ac',
        name: 'Smart Mini-Split AC',
        room: 'Tech Office',
        roomKey: 'office',
        type: 'climate',
        baseWatt: 1000,
        isOn: true,
        setpoint: 23,
        icon: '❄️',
        sliderMin: 16,
        sliderMax: 30,
        sliderUnit: '°C',
        controlType: 'temp'
      },

      // 5. Utility & Garage
      ev_charger: {
        id: 'ev_charger',
        name: 'Level-2 Smart EV Charger (7.4 kW)',
        room: 'Garage & Utility',
        roomKey: 'garage',
        type: 'ev',
        baseWatt: 7400,
        isOn: true, // Charging during day/peak
        rateKw: 7.4,
        icon: '🚗',
        sliderMin: 1.4,
        sliderMax: 7.4,
        sliderUnit: 'kW',
        controlType: 'ev_rate'
      },
      water_heater: {
        id: 'water_heater',
        name: 'Hybrid Heat Pump Water Heater',
        room: 'Garage & Utility',
        roomKey: 'garage',
        type: 'heating',
        baseWatt: 1400,
        isOn: false,
        powerFactor: 1.0,
        icon: '♨️',
        controlType: 'switch'
      }
    };

    // Room Occupancy
    this.occupancy = {
      living: true,
      kitchen: true,
      bedroom: false, // unoccupied by default to demonstrate ghost load
      office: true,
      garage: false
    };

    this.initUI();
    this.updateCalculations();
  }

  initUI() {
    this.renderRooms();
    this.bindControls();
  }

  renderRooms() {
    const grid = document.getElementById('estateRoomsGrid');
    if (!grid) return;

    const roomDefs = [
      { key: 'living', name: 'Living Room', icon: '🛋️' },
      { key: 'kitchen', name: 'Modern Kitchen', icon: '🍳' },
      { key: 'bedroom', name: 'Master Suite', icon: '🛏️' },
      { key: 'office', name: 'Tech Work Office', icon: '🖥️' },
      { key: 'garage', name: 'Garage & Utility', icon: '🚗' }
    ];

    let html = '';

    roomDefs.forEach(r => {
      const isOccupied = this.occupancy[r.key];
      const roomApps = Object.values(this.appliances).filter(a => a.roomKey === r.key);

      html += `
        <div class="room-card ${isOccupied ? 'active-load' : ''}" id="room_card_${r.key}">
          <div class="room-header">
            <div class="room-title">
              <span>${r.icon}</span> ${r.name}
            </div>
            <div class="occupancy-toggle ${isOccupied ? 'occupied' : ''}" 
                 onclick="window.simulator.toggleOccupancy('${r.key}')" 
                 id="occ_btn_${r.key}">
              <span>${isOccupied ? '🟢 Occupied' : '⚪ Vacant'}</span>
            </div>
          </div>
          <div class="appliance-list">
            ${roomApps.map(app => this.renderApplianceNode(app)).join('')}
          </div>
        </div>
      `;
    });

    grid.innerHTML = html;
  }

  renderApplianceNode(app) {
    let controlsHtml = '';

    if (app.controlType === 'temp') {
      controlsHtml = `
        <div class="appliance-controls" id="ctrl_${app.id}">
          <span class="control-label">Thermostat:</span>
          <input type="range" class="range-slider" min="${app.sliderMin}" max="${app.sliderMax}" 
                 value="${app.setpoint}" 
                 oninput="window.simulator.updateApplianceValue('${app.id}', this.value, 'setpoint')" />
          <span class="control-val" id="val_${app.id}">${app.setpoint}°C</span>
        </div>
      `;
    } else if (app.controlType === 'dimmer') {
      controlsHtml = `
        <div class="appliance-controls" id="ctrl_${app.id}">
          <span class="control-label">Brightness:</span>
          <input type="range" class="range-slider" min="${app.sliderMin}" max="${app.sliderMax}" 
                 value="${app.dimmerPct}" 
                 oninput="window.simulator.updateApplianceValue('${app.id}', this.value, 'dimmerPct')" />
          <span class="control-val" id="val_${app.id}">${app.dimmerPct}%</span>
        </div>
      `;
    } else if (app.controlType === 'ev_rate') {
      controlsHtml = `
        <div class="appliance-controls" id="ctrl_${app.id}">
          <span class="control-label">Charge Rate:</span>
          <input type="range" class="range-slider" min="1.4" max="7.4" step="0.2"
                 value="${app.rateKw}" 
                 oninput="window.simulator.updateApplianceValue('${app.id}', this.value, 'rateKw')" />
          <span class="control-val" id="val_${app.id}">${app.rateKw} kW</span>
        </div>
      `;
    }

    return `
      <div class="appliance-node" id="node_${app.id}">
        <div class="appliance-node-top">
          <div class="appliance-info">
            <span class="appliance-icon">${app.icon}</span>
            <div>
              <div class="appliance-name">${app.name}</div>
              <div class="appliance-power ${app.isOn ? '' : 'off'}" id="pwr_${app.id}">
                ${app.isOn ? 'Calculating...' : '0.0 W (OFF)'}
              </div>
            </div>
          </div>
          <label class="switch">
            <input type="checkbox" ${app.isOn ? 'checked' : ''} 
                   onchange="window.simulator.toggleAppliance('${app.id}', this.checked)" />
            <span class="slider-round"></span>
          </label>
        </div>
        ${controlsHtml}
      </div>
    `;
  }

  bindControls() {
    // Weather & Time inputs
    const timeSlider = document.getElementById('simTimeSlider');
    if (timeSlider) {
      timeSlider.addEventListener('input', (e) => {
        this.timeHour = parseInt(e.target.value);
        const timeLabel = document.getElementById('simTimeDisplay');
        if (timeLabel) timeLabel.innerText = `${this.timeHour.toString().padStart(2, '0')}:00`;
        this.updateCalculations();
      });
    }

    const tempSlider = document.getElementById('simTempSlider');
    if (tempSlider) {
      tempSlider.addEventListener('input', (e) => {
        this.outdoorTemp = parseInt(e.target.value);
        const tempLabel = document.getElementById('simTempDisplay');
        if (tempLabel) tempLabel.innerText = `${this.outdoorTemp}°C`;
        this.updateCalculations();
      });
    }
  }

  toggleOccupancy(roomKey) {
    this.occupancy[roomKey] = !this.occupancy[roomKey];
    const btn = document.getElementById(`occ_btn_${roomKey}`);
    const card = document.getElementById(`room_card_${roomKey}`);
    
    if (btn) {
      btn.className = `occupancy-toggle ${this.occupancy[roomKey] ? 'occupied' : ''}`;
      btn.innerHTML = `<span>${this.occupancy[roomKey] ? '🟢 Occupied' : '⚪ Vacant'}</span>`;
    }
    if (card) {
      if (this.occupancy[roomKey]) {
        card.classList.add('active-load');
      } else {
        card.classList.remove('active-load');
      }
    }
    this.updateCalculations();
  }

  toggleAppliance(appId, isChecked) {
    if (this.appliances[appId]) {
      this.appliances[appId].isOn = isChecked;
      this.updateCalculations();
    }
  }

  updateApplianceValue(appId, val, prop) {
    if (this.appliances[appId]) {
      this.appliances[appId][prop] = parseFloat(val);
      const valDisplay = document.getElementById(`val_${appId}`);
      if (valDisplay) {
        if (prop === 'setpoint') valDisplay.innerText = `${val}°C`;
        else if (prop === 'dimmerPct') valDisplay.innerText = `${val}%`;
        else if (prop === 'rateKw') valDisplay.innerText = `${val} kW`;
      }
      this.updateCalculations();
    }
  }

  calculateAppliancePower(app) {
    if (!app.isOn) return 0;

    if (app.type === 'climate') {
      const setpoint = app.setpoint || 24;
      const diff = Math.max(0, this.outdoorTemp - setpoint);
      // Base thermal formula: Power scales with delta T between outdoor and setpoint
      return Math.round(app.baseWatt * (0.65 + diff * 0.16));
    } else if (app.type === 'lighting') {
      const dim = (app.dimmerPct || 100) / 100;
      return Math.round(app.baseWatt * dim);
    } else if (app.type === 'ev') {
      return Math.round((app.rateKw || 7.4) * 1000);
    } else {
      return Math.round(app.baseWatt * (app.powerFactor || 1.0));
    }
  }

  updateCalculations() {
    let totalHomeWatts = 0;
    const wasteList = [];

    const isPeakTariff = (this.timeHour >= 18 && this.timeHour <= 22);
    const tariffRate = isPeakTariff ? 12.5 : 7.5; // INR per kWh

    // Calculate individual appliances
    Object.values(this.appliances).forEach(app => {
      const watts = this.calculateAppliancePower(app);
      totalHomeWatts += watts;

      // Update UI power node badge
      const pwrBadge = document.getElementById(`pwr_${app.id}`);
      if (pwrBadge) {
        if (app.isOn) {
          pwrBadge.className = 'appliance-power';
          pwrBadge.innerText = watts >= 1000 ? `${(watts / 1000).toFixed(2)} kW` : `${watts} W`;
        } else {
          pwrBadge.className = 'appliance-power off';
          pwrBadge.innerText = '0.0 W (OFF)';
        }
      }

      // Check waste logic
      const isRoomOccupied = this.occupancy[app.roomKey];
      if (app.isOn) {
        if (app.type === 'climate' && app.setpoint < 22) {
          wasteList.push({
            title: `Overcooling: ${app.name}`,
            desc: `Set to ${app.setpoint}°C in ${app.room}. Raising to 24°C saves ~28% power without comfort loss.`,
            appId: app.id
          });
        }
        if (app.type === 'lighting' && !isRoomOccupied) {
          wasteList.push({
            title: `Ghost Light: ${app.name}`,
            desc: `Lights powered on in an empty room (${app.room}).`,
            appId: app.id
          });
        }
        if (app.type === 'ev' && isPeakTariff) {
          wasteList.push({
            title: `Peak Tariff Charging: ${app.name}`,
            desc: `High 7.4kW load during peak tariff hours (₹12.5/unit). Delay charging to off-peak night.`,
            appId: app.id
          });
        }
      }
    });

    const totalKw = totalHomeWatts / 1000;

    // Solar calculation
    let solarKw = 0;
    if (this.solarActive && this.timeHour >= 6 && this.timeHour <= 18 && this.isSunny) {
      const solarCurve = Math.sin((this.timeHour - 6) * Math.PI / 12);
      solarKw = Math.max(0, this.solarCapacityKw * solarCurve);
    }

    const netGridKw = Math.max(0, totalKw - solarKw);
    const solarExportKw = Math.max(0, solarKw - totalKw);
    const costPerHour = (netGridKw * tariffRate).toFixed(2);
    const co2PerHour = (netGridKw * 0.82).toFixed(3);

    // Update Telemetry Panel Elements
    const totalPwrElem = document.getElementById('simTotalPower');
    if (totalPwrElem) totalPwrElem.innerText = totalKw.toFixed(2);

    const solarGenElem = document.getElementById('simSolarGen');
    if (solarGenElem) solarGenElem.innerText = solarKw.toFixed(2);

    const netGridElem = document.getElementById('simNetGrid');
    if (netGridElem) netGridElem.innerText = netGridKw.toFixed(2);

    const costElem = document.getElementById('simCostRate');
    if (costElem) costElem.innerText = `₹${costPerHour}/hr`;

    const co2Elem = document.getElementById('simCo2Rate');
    if (co2Elem) co2Elem.innerText = `${co2PerHour} kg/hr`;

    const tariffTag = document.getElementById('simTariffTag');
    if (tariffTag) {
      tariffTag.className = `badge ${isPeakTariff ? 'badge-critical' : 'badge-low'}`;
      tariffTag.innerText = isPeakTariff ? 'Peak Tariff (₹12.5/kWh)' : 'Standard (₹7.5/kWh)';
    }

    // Render Waste Feed
    const wasteContainer = document.getElementById('simWasteFeed');
    if (wasteContainer) {
      if (wasteList.length === 0) {
        wasteContainer.innerHTML = `
          <div style="text-align:center; padding: 1.5rem 0.5rem; color: var(--accent-emerald);">
            <div style="font-size:1.8rem; margin-bottom:0.4rem;">🌱</div>
            <div style="font-weight:700; font-size:0.9rem;">Clean Energy Balance</div>
            <div style="font-size:0.75rem; color: var(--text-dim); margin-top:0.2rem;">No major energy leaks detected. System is running near optimum efficiency.</div>
          </div>
        `;
      } else {
        wasteContainer.innerHTML = wasteList.map(w => `
          <div class="waste-item">
            <div class="waste-item-title">⚠️ ${w.title}</div>
            <div class="waste-item-desc">${w.desc}</div>
          </div>
        `).join('');
      }
    }
  }

  /**
   * AI ECO-OPTIMIZER / AUTO-BALANCE
   * Instantly rebalances all household appliances according to thermodynamic & tariff rules.
   */
  aiAutoOptimize() {
    const isPeakTariff = (this.timeHour >= 18 && this.timeHour <= 22);

    // 1. Thermostat reset to 24.5°C
    ['living_ac', 'bed_ac', 'office_ac'].forEach(acId => {
      if (this.appliances[acId] && this.appliances[acId].isOn) {
        this.appliances[acId].setpoint = 24;
        const valElem = document.getElementById(`val_${acId}`);
        if (valElem) valElem.innerText = '24°C';
      }
    });

    // 2. Shut off lights & entertainment in vacant rooms
    Object.keys(this.occupancy).forEach(roomKey => {
      if (!this.occupancy[roomKey]) {
        Object.values(this.appliances).forEach(app => {
          if (app.roomKey === roomKey && (app.type === 'lighting' || app.id === 'living_tv')) {
            app.isOn = false;
          }
        });
      }
    });

    // 3. Defer EV charger during peak tariff or throttle down
    if (this.appliances.ev_charger && this.appliances.ev_charger.isOn && isPeakTariff) {
      this.appliances.ev_charger.isOn = false; // Delay to midnight
    }

    // 4. Dim daytime lights if sunny
    if (this.isSunny && this.timeHour >= 10 && this.timeHour <= 16) {
      ['living_lights', 'bed_lights'].forEach(lId => {
        if (this.appliances[lId] && this.appliances[lId].isOn) {
          this.appliances[lId].dimmerPct = 35;
          const valElem = document.getElementById(`val_${lId}`);
          if (valElem) valElem.innerText = '35%';
        }
      });
    }

    // Re-render rooms to sync checkboxes and sliders
    this.renderRooms();
    this.updateCalculations();

    // Show Savings Modal
    this.showOptimizationToast();
  }

  showOptimizationToast() {
    const toast = document.getElementById('optToast');
    if (!toast) return;

    toast.style.display = 'block';
    setTimeout(() => {
      toast.style.display = 'none';
    }, 6000);
  }
}

// Attach to global window
window.addEventListener('DOMContentLoaded', () => {
  window.simulator = new SmartEstateSimulator();
});
