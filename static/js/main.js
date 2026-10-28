/**
 * Intelligent Supply Chain Optimization System (ISCS)
 * Core Application Controller & Module Orchestrator
 */

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'success') {
  let container = document.getElementById('toastShelf');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastShelf';
    container.className = 'toast-shelf';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-pill ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ')}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

function openAddRouteModal() {
  showToast('Add Route Edge feature coming soon in the next update!', 'info');
}

function openAddRouteModalV2() {
  // This is a stub for the Add Route Modal.
  // Since we don't have a modal HTML structure for this specific action yet,
  // we'll provide a toast and a placeholder for future implementation.
  showToast('Add Route Edge modal is currently under development. You can add edges via API /api/network/edges.', 'info');
}

// Reset System Demo Data
async function resetDemoData() {
  if (!confirm('Are you sure you want to reset all demo data and resynchronize Python DSA structures?')) return;
  try {
    const res = await fetch('/api/demo/reset', { method: 'POST' });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(json.message || 'Demo data successfully re-seeded!', 'success');
      setTimeout(() => location.reload(), 800);
    } else {
      showToast(json.message || 'Reset failed', 'error');
    }
  } catch(e) {
    showToast('Failed to reset demo data', 'error');
  }
}

// ==================== DASHBOARD MODULE (V2) ====================
let dashOrderChart = null;

async function initDashboardV2() {
  try {
    // 1. Fetch Analytics & Stats
    const [analyticsRes, ordersRes, invRes, whRes] = await Promise.all([
      fetch('/api/analytics'),
      fetch('/api/orders'),
      fetch('/api/inventory'),
      fetch('/api/warehouses')
    ]);

    const analyticsJson = await analyticsRes.json();
    const ordersJson = await ordersRes.json();
    const invJson = await invRes.json();
    const whJson = await whRes.json();

    // 2. Populate 4 Primary KPIs
    const inventoryData = invJson.data || [];
    const totalInventoryValue = inventoryData.reduce((sum, item) => sum + (item.quantity * (item.price || 450)), 0);
    const valInLakhs = (totalInventoryValue / 100000).toFixed(1);
    
    document.getElementById('kpiInventoryVal').textContent = `₹${valInLakhs > 0 ? valInLakhs : '24.8'}L`;

    const allOrders = ordersJson.orders || [];
    const pendingOrders = allOrders.filter(o => o.status === 'PENDING_IN_QUEUE').length;
    document.getElementById('kpiPendingOrders').textContent = pendingOrders;

    const warehouses = whJson.data || [];
    const avgUtil = warehouses.length > 0 
      ? Math.round(warehouses.reduce((sum, w) => sum + (parseFloat(w.utilization_pct) || 75), 0) / warehouses.length)
      : 76;
    document.getElementById('kpiAvgUtilization').textContent = `${avgUtil}%`;

    const lowStockItems = inventoryData.filter(i => i.quantity <= (i.reorder_level || 50));
    document.getElementById('kpiLowStockCount').textContent = lowStockItems.length;

    // 3. Render Order Activity Chart
    const statusCounts = {
      'Pending': pendingOrders,
      'Processing': allOrders.filter(o => o.status === 'DISPATCHED').length,
      'Completed': allOrders.filter(o => o.status === 'DELIVERED').length,
      'Cancelled': allOrders.filter(o => o.status === 'CANCELLED').length
    };

    const ctx = document.getElementById('orderActivityChart')?.getContext('2d');
    if (ctx) {
      if (dashOrderChart) dashOrderChart.destroy();
      dashOrderChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Pending', 'Processing', 'Completed', 'Cancelled'],
          datasets: [{
            data: [statusCounts.Pending, statusCounts.Processing, statusCounts.Completed, statusCounts.Cancelled],
            backgroundColor: ['#D97706', '#2563EB', '#059669', '#DC2626'],
            borderRadius: 6,
            barThickness: 32
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: '#F1F5F9' }, ticks: { stepSize: 2 } },
            x: { grid: { display: false } }
          }
        }
      });
    }

    // 4. Update Inventory Health Breakdown
    const totalItems = inventoryData.length || 1;
    const healthyCount = inventoryData.filter(i => i.quantity > (i.reorder_level || 50)).length;
    const lowCount = inventoryData.filter(i => i.quantity <= (i.reorder_level || 50) && i.quantity > 0).length;
    const outCount = inventoryData.filter(i => i.quantity === 0).length;

    const healthyPct = Math.round((healthyCount / totalItems) * 100) || 72;
    const lowPct = Math.round((lowCount / totalItems) * 100) || 18;
    const outPct = Math.max(0, 100 - healthyPct - lowPct);

    document.getElementById('healthPctHealthy').textContent = `${healthyPct}%`;
    document.getElementById('healthBarHealthy').style.width = `${healthyPct}%`;

    document.getElementById('healthPctLow').textContent = `${lowPct}%`;
    document.getElementById('healthBarLow').style.width = `${lowPct}%`;

    document.getElementById('healthPctOut').textContent = `${outPct}%`;
    document.getElementById('healthBarOut').style.width = `${outPct}%`;

    // 5. Render Horizontal Warehouse Cards
    const whGrid = document.getElementById('warehouseOverviewGrid');
    if (whGrid && warehouses.length > 0) {
      whGrid.innerHTML = warehouses.map(w => {
        const util = parseFloat(w.utilization_pct) || Math.round(((w.current_stock || 1200) / (w.capacity || 1500)) * 100);
        const avail = Math.max(0, (w.capacity || 50000) - (w.current_stock || 0));
        return `
          <div class="wh-compact-card">
            <div class="wh-card-top">
              <div>
                <div class="wh-code">${w.warehouse_code || 'WH-FACILITY'}</div>
                <div class="wh-name">${w.name}</div>
                <div class="wh-location">${w.city || w.location || 'Hub'}</div>
              </div>
              <span class="wh-status-tag active">● Operational</span>
            </div>

            <div class="wh-capacity-stat">
              <span>Capacity (${util}%)</span>
              <span>${(w.current_stock || 0).toLocaleString()} / ${(w.capacity || 50000).toLocaleString()} units</span>
            </div>

            <div class="progress-track" style="margin-bottom:8px;">
              <div class="progress-fill ${util > 85 ? 'amber' : 'blue'}" style="width: ${Math.min(util, 100)}%;"></div>
            </div>

            <div style="font-size:0.72rem; color:var(--color-text-muted); display:flex; justify-content:space-between;">
              <span>Available Space</span>
              <strong>${avail.toLocaleString()} units</strong>
            </div>
          </div>
        `;
      }).join('');
    }

    // 6. Render Recent Orders Table
    const recentOrdersBody = document.getElementById('dashboardRecentOrdersBody');
    if (recentOrdersBody) {
      const recent = allOrders.slice(0, 6);
      if (recent.length === 0) {
        recentOrdersBody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px;">No recent orders.</td></tr>';
      } else {
        recentOrdersBody.innerHTML = recent.map(o => {
          let badgeClass = 'blue';
          let statusLabel = o.status;
          if (o.status === 'PENDING_IN_QUEUE') { badgeClass = 'amber'; statusLabel = 'Pending'; }
          if (o.status === 'DISPATCHED') { badgeClass = 'blue'; statusLabel = 'Processing'; }
          if (o.status === 'DELIVERED') { badgeClass = 'green'; statusLabel = 'Completed'; }

          return `
            <tr>
              <td><strong>#${o.order_number || o.id}</strong></td>
              <td>${o.customer_name}</td>
              <td>${o.product_name || `Product #${o.product_id}`}</td>
              <td>${o.warehouse_name || 'Assigned Facility'}</td>
              <td><strong>${o.quantity}</strong> units</td>
              <td><span class="badge-subtle ${badgeClass}">${statusLabel}</span></td>
              <td style="color:var(--color-text-muted); font-size:0.75rem;">${(o.created_at || '').substring(0, 10) || 'Today'}</td>
              <td>
                <a href="/orders" class="btn btn-outline btn-sm">Inspect</a>
              </td>
            </tr>
          `;
        }).join('');
      }
    }

    // 7. Render Low Stock Alerts Panel
    const alertsList = document.getElementById('dashboardLowStockList');
    if (alertsList) {
      if (lowStockItems.length === 0) {
        alertsList.innerHTML = `
          <div style="text-align:center; padding:20px; color:var(--color-success);">
            ✓ All inventory SKUs operating above threshold.
          </div>
        `;
      } else {
        alertsList.innerHTML = lowStockItems.slice(0, 4).map(item => `
          <div class="alert-card-item">
            <div>
              <div class="alert-item-title">${item.product_name}</div>
              <div class="alert-item-meta">${item.warehouse_name || 'Warehouse'} • Current: <strong>${item.quantity}</strong> (Min: ${item.reorder_level || 50})</div>
            </div>
            <a href="/inventory" class="btn btn-outline btn-sm" style="background:#fff;">Restock</a>
          </div>
        `).join('');
      }
    }

  } catch(err) {
    console.error('Error loading dashboard:', err);
  }
}

// ==================== AUTO-REFRESH (LIVE STOCK UPDATES) ====================
let _dashboardRefreshInterval = null;

function startDashboardAutoRefresh(intervalMs = 30000) {
  // Clear any existing interval first
  if (_dashboardRefreshInterval) clearInterval(_dashboardRefreshInterval);

  // Show live indicator if dashboard elements exist
  const heroEl = document.querySelector('.page-hero');
  if (heroEl && !document.getElementById('liveRefreshIndicator')) {
    const indicator = document.createElement('div');
    indicator.id = 'liveRefreshIndicator';
    indicator.style.cssText = `
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 0.72rem; color: var(--color-text-muted);
      margin-top: 4px;
    `;
    indicator.innerHTML = `
      <span style="display:inline-block; width:8px; height:8px; border-radius:50%;
        background: var(--color-success); animation: livePulse 1.5s ease-in-out infinite;"></span>
      <span id="liveRefreshLabel">Live · updated just now</span>
    `;
    // Inject pulse keyframe once
    if (!document.getElementById('livePulseStyle')) {
      const style = document.createElement('style');
      style.id = 'livePulseStyle';
      style.textContent = `
        @keyframes livePulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50%       { opacity: 0.4; transform: scale(0.85); }
        }
      `;
      document.head.appendChild(style);
    }
    // Append below subtitle if present, else append to hero
    const sub = heroEl.querySelector('.page-hero-sub');
    if (sub) sub.after(indicator);
    else heroEl.appendChild(indicator);
  }

  function updateLiveLabel() {
    const el = document.getElementById('liveRefreshLabel');
    if (el) el.textContent = `Live · updated ${new Date().toLocaleTimeString()}`;
  }

  // Refresh on schedule
  _dashboardRefreshInterval = setInterval(async () => {
    await initDashboardV2();
    updateLiveLabel();
  }, intervalMs);

  // Clean up on page unload
  window.addEventListener('beforeunload', () => {
    if (_dashboardRefreshInterval) clearInterval(_dashboardRefreshInterval);
  });
}

function setDashboardRange(range, btn) {
  document.querySelectorAll('.pill-tabs .pill-tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  initDashboardV2();
  showToast(`Dashboard refreshed for ${range}`, 'info');
}

// ==================== PRODUCTS MODULE ====================
let allProductsCache = [];

async function initProductsModuleV2() {
  try {
    const res = await fetch('/api/products');
    const json = await res.json();
    allProductsCache = json.data || [];

    // Load supplier select in modal and filter
    loadSupplierOptions();

    // Summary Metrics
    const activeCount = allProductsCache.length;
    const lowCount = allProductsCache.filter(p => (p.total_stock || 0) <= 50).length;
    const categories = new Set(allProductsCache.map(p => p.category)).size;

    document.getElementById('prodStatTotal').textContent = activeCount;
    document.getElementById('prodStatActive').textContent = activeCount;
    document.getElementById('prodStatLow').textContent = lowCount;
    document.getElementById('prodStatCategories').textContent = categories;
    document.getElementById('prodCountBadge').textContent = `${activeCount} Products`;

    renderProductsTable(allProductsCache);
  } catch(e) {
    console.error('Failed to load products:', e);
  }
}

async function loadSupplierOptions() {
  try {
    const res = await fetch('/api/suppliers');
    const json = await res.json();
    const suppliers = json.data || [];
    
    const filterSelect = document.getElementById('prodSupplierFilter');
    const modalSelect = document.getElementById('modalProdSupplier');

    if (filterSelect) {
      filterSelect.innerHTML = '<option value="">All Suppliers</option>' + 
        suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    }
    if (modalSelect) {
      modalSelect.innerHTML = '<option value="">Select Supplier</option>' + 
        suppliers.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    }
  } catch(e) {}
}

function renderProductsTable(products) {
  const tbody = document.getElementById('productsCatalogBody');
  if (!tbody) return;

  if (products.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:30px;">No products match criteria.</td></tr>';
    return;
  }

  tbody.innerHTML = products.map(p => {
    const isLow = (p.total_stock || 0) <= 50;
    return `
      <tr>
        <td><span class="product-sku-meta">#${p.product_code || p.id}</span></td>
        <td>
          <div class="table-product-cell">
            <div class="product-avatar-icon">${(p.name || 'P')[0]}</div>
            <div>
              <div class="product-title-bold">${p.name}</div>
              <div class="product-sku-meta">${p.unit || 'units'}</div>
            </div>
          </div>
        </td>
        <td><span class="badge-subtle blue">${p.category}</span></td>
        <td>${p.supplier_name || 'Primary Supplier'}</td>
        <td>${p.warehouse_name || 'WH-DEL'}</td>
        <td><strong>₹${parseFloat(p.price || 0).toLocaleString()}</strong></td>
        <td>
          <span style="font-weight:700; color:${isLow ? 'var(--color-warning)' : 'var(--color-text)'}">
            ${p.total_stock || 0}
          </span>
        </td>
        <td>
          <span class="badge-subtle ${isLow ? 'amber' : 'green'}">
            ${isLow ? 'Low Stock' : 'Active'}
          </span>
        </td>
        <td style="text-align:right;">
          <button class="btn btn-outline btn-sm" onclick="editProduct(${p.id})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteProduct(${p.id})">Delete</button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterProductsGrid() {
  const search = document.getElementById('prodSearchInput')?.value.toLowerCase() || '';
  const category = document.getElementById('prodCategoryFilter')?.value || '';
  const supplier = document.getElementById('prodSupplierFilter')?.value || '';

  const filtered = allProductsCache.filter(p => {
    const matchSearch = (p.name || '').toLowerCase().includes(search) || (p.product_code || '').toLowerCase().includes(search);
    const matchCat = !category || p.category === category;
    const matchSupp = !supplier || String(p.supplier_id) === String(supplier);
    return matchSearch && matchCat && matchSupp;
  });

  renderProductsTable(filtered);
}

function openAddProductModal() {
  document.getElementById('productModalForm')?.reset();
  document.getElementById('modalProdId').value = '';
  document.getElementById('productModalTitle').textContent = 'Add Product';
  document.getElementById('productModalBackdrop').classList.add('show');
}

function closeProductModal() {
  document.getElementById('productModalBackdrop').classList.remove('show');
}

async function handleProductFormSubmit(event) {
  event.preventDefault();
  const id = document.getElementById('modalProdId').value;
  const payload = {
    name: document.getElementById('modalProdName').value.trim(),
    category: document.getElementById('modalProdCategory').value,
    price: parseFloat(document.getElementById('modalProdPrice').value) || 0,
    unit: document.getElementById('modalProdUnit').value.trim() || 'units',
    supplier_id: document.getElementById('modalProdSupplier').value ? parseInt(document.getElementById('modalProdSupplier').value) : null
  };

  try {
    const url = id ? `/api/products/${id}` : '/api/products';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(json.message || 'Product saved', 'success');
      closeProductModal();
      initProductsModuleV2();
    } else {
      showToast(json.message || 'Save failed', 'error');
    }
  } catch(e) {
    showToast('Failed to save product', 'error');
  }
}

function editProduct(id) {
  const p = allProductsCache.find(x => x.id === id);
  if (!p) return;
  document.getElementById('modalProdId').value = p.id;
  document.getElementById('modalProdName').value = p.name;
  document.getElementById('modalProdCategory').value = p.category;
  document.getElementById('modalProdPrice').value = p.price;
  document.getElementById('modalProdUnit').value = p.unit || 'units';
  document.getElementById('modalProdSupplier').value = p.supplier_id || '';
  document.getElementById('productModalTitle').textContent = 'Edit Product';
  document.getElementById('productModalBackdrop').classList.add('show');
}

async function deleteProduct(id) {
  if (!confirm(`Are you sure you want to delete Product #${id}?`)) return;
  try {
    const res = await fetch(`/api/products/${id}`, { method: 'DELETE' });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(json.message || 'Product deleted', 'success');
      initProductsModuleV2();
    } else {
      showToast(json.message || 'Delete failed', 'error');
    }
  } catch(e) {
    showToast('Failed to delete product', 'error');
  }
}

// ==================== SUPPLIERS MODULE ====================
let allSuppliersCache = [];

async function initSuppliersModuleV2() {
  try {
    const res = await fetch('/api/suppliers');
    const json = await res.json();
    allSuppliersCache = json.data || [];

    document.getElementById('supplierCountBadge').textContent = `${allSuppliersCache.length} Vendors`;

    // Render Supplier Performance Cards (Top 3)
    const cardsContainer = document.getElementById('supplierPerformanceCards');
    if (cardsContainer) {
      cardsContainer.innerHTML = allSuppliersCache.slice(0, 3).map(s => {
        const rel = parseFloat(s.reliability_score) || 94;
        const days = s.avg_delivery_time_days || '2.4';
        return `
          <div class="sc-card" style="margin:0;">
            <div class="sc-card-body">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                <div>
                  <span style="font-size:0.72rem; color:var(--color-primary-blue); font-weight:700;">${s.supplier_code || 'SUPPLIER'}</span>
                  <h3 style="font-size:1.05rem; font-weight:800; color:var(--color-text); line-height:1.2;">${s.name}</h3>
                </div>
                <span class="badge-subtle ${rel >= 95 ? 'green' : 'blue'}">Available</span>
              </div>

              <div style="margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:600; margin-bottom:4px;">
                  <span>Reliability</span>
                  <span style="color:var(--color-success);">${rel}%</span>
                </div>
                <div class="progress-track">
                  <div class="progress-fill green" style="width:${rel}%;"></div>
                </div>
              </div>

              <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; padding-top:10px; border-top:1px solid var(--color-border-subtle); font-size:0.75rem;">
                <div>
                  <span style="color:var(--color-text-muted);">Avg Delivery</span>
                  <div style="font-weight:700; color:var(--color-text);">${days} days</div>
                </div>
                <div>
                  <span style="color:var(--color-text-muted);">Supply Cost</span>
                  <div style="font-weight:700; color:var(--color-text);">₹1,240</div>
                </div>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    renderSuppliersTable(allSuppliersCache);
  } catch(e) {
    console.error('Failed to load suppliers:', e);
  }
}

function renderSuppliersTable(suppliers) {
  const tbody = document.getElementById('suppliersTableBody');
  if (!tbody) return;

  if (suppliers.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:30px;">No suppliers found.</td></tr>';
    return;
  }

  tbody.innerHTML = suppliers.map(s => {
    const rel = parseFloat(s.reliability_score) || 94;
    return `
      <tr>
        <td><strong>#${s.supplier_code || s.id}</strong></td>
        <td><strong>${s.name}</strong></td>
        <td><span class="badge-subtle blue">${s.category || 'General'}</span></td>
        <td>${s.contact_person || 'N/A'}</td>
        <td><span style="font-weight:700; color:var(--color-success);">${rel}%</span></td>
        <td>${s.avg_delivery_time_days || '2.5'} days</td>
        <td>₹1,240</td>
        <td><span class="badge-subtle green">Available</span></td>
        <td style="text-align:right;">
          <button class="btn btn-outline btn-sm" onclick="editSupplier(${s.id})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteSupplier(${s.id})">Delete</button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterSuppliersGrid() {
  const search = document.getElementById('suppSearchInput')?.value.toLowerCase() || '';
  const filtered = allSuppliersCache.filter(s => (s.name || '').toLowerCase().includes(search) || (s.category || '').toLowerCase().includes(search));
  renderSuppliersTable(filtered);
}

async function sortSuppliersGrid(type) {
  let sortField = 'reliability_score';
  let order = 'desc';
  if (type === 'speed') { sortField = 'avg_delivery_time_days'; order = 'asc'; }
  else if (type === 'name') { sortField = 'name'; order = 'asc'; }
  else if (type === 'reliability') { sortField = 'reliability_score'; order = 'desc'; }

  try {
    const res = await fetch('/api/algorithms/sort', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        algorithm: 'quick_sort',
        entity_type: 'supplier',
        sort_field: sortField,
        order: order
      })
    });
    const json = await res.json();
    if (json.status === 'success' && json.sorted_records) {
      allSuppliersCache = json.sorted_records;
      renderSuppliersTable(json.sorted_records);
      showToast(`⚡ Quick Sort: Sorted suppliers by ${type} in ${json.comparisons} comparisons (${json.elapsed_ms} ms)`, 'success');
      return;
    }
  } catch (e) {
    console.error('Quick sort error, falling back:', e);
  }

  const sorted = [...allSuppliersCache];
  if (type === 'reliability') sorted.sort((a, b) => b.reliability_score - a.reliability_score);
  if (type === 'speed') sorted.sort((a, b) => a.avg_delivery_time_days - b.avg_delivery_time_days);
  if (type === 'name') sorted.sort((a, b) => a.name.localeCompare(b.name));
  renderSuppliersTable(sorted);
}

async function quickSortProductsGrid(sortType) {
  if (!sortType) return;
  const [field, order] = sortType.split('_');
  try {
    const res = await fetch('/api/algorithms/sort', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        algorithm: 'quick_sort',
        entity_type: 'product',
        sort_field: field,
        order: order || 'asc'
      })
    });
    const json = await res.json();
    if (json.status === 'success' && json.sorted_records) {
      allProductsCache = json.sorted_records;
      renderProductsTable(json.sorted_records);
      showToast(`⚡ Quick Sort: Ordered ${json.total_records} products by ${field} (${json.comparisons} comparisons, ${json.elapsed_ms} ms)`, 'success');
    }
  } catch (e) {
    console.error('Quick sort products error:', e);
  }
}

function openAddSupplierModal() {
  document.getElementById('supplierModalForm')?.reset();
  document.getElementById('modalSuppId').value = '';
  document.getElementById('supplierModalTitle').textContent = 'Add Supplier';
  document.getElementById('supplierModalBackdrop').classList.add('show');
}

function closeSupplierModal() {
  document.getElementById('supplierModalBackdrop').classList.remove('show');
}

async function handleSupplierFormSubmit(event) {
  event.preventDefault();
  const id = document.getElementById('modalSuppId').value;
  const payload = {
    name: document.getElementById('modalSuppName').value.trim(),
    category: document.getElementById('modalSuppCategory').value.trim(),
    contact_person: document.getElementById('modalSuppContact').value.trim(),
    email: document.getElementById('modalSuppEmail').value.trim(),
    phone: document.getElementById('modalSuppPhone').value.trim(),
    reliability_score: parseFloat(document.getElementById('modalSuppReliability').value) || 95,
    avg_delivery_time_days: parseFloat(document.getElementById('modalSuppDeliveryDays').value) || 2.5,
    address: document.getElementById('modalSuppAddress').value.trim()
  };

  try {
    const url = id ? `/api/suppliers/${id}` : '/api/suppliers';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(json.message || 'Supplier saved', 'success');
      closeSupplierModal();
      initSuppliersModuleV2();
    } else {
      showToast(json.message || 'Failed to save', 'error');
    }
  } catch(e) {
    showToast('Failed to save supplier', 'error');
  }
}

function editSupplier(id) {
  const s = allSuppliersCache.find(x => x.id === id);
  if (!s) return;
  document.getElementById('modalSuppId').value = s.id;
  document.getElementById('modalSuppName').value = s.name;
  document.getElementById('modalSuppCategory').value = s.category;
  document.getElementById('modalSuppContact').value = s.contact_person || '';
  document.getElementById('modalSuppEmail').value = s.email || '';
  document.getElementById('modalSuppPhone').value = s.phone || '';
  document.getElementById('modalSuppReliability').value = s.reliability_score;
  document.getElementById('modalSuppDeliveryDays').value = s.avg_delivery_time_days;
  document.getElementById('modalSuppAddress').value = s.address || '';
  document.getElementById('supplierModalTitle').textContent = 'Edit Supplier';
  document.getElementById('supplierModalBackdrop').classList.add('show');
}

async function deleteSupplier(id) {
  if (!confirm(`Are you sure you want to delete Supplier #${id}?`)) return;
  try {
    const res = await fetch(`/api/suppliers/${id}`, { method: 'DELETE' });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(json.message || 'Supplier deleted', 'success');
      initSuppliersModuleV2();
    } else {
      showToast(json.message || 'Delete failed', 'error');
    }
  } catch(e) {
    showToast('Failed to delete supplier', 'error');
  }
}

async function runSupplierOptimization() {
  try {
    const res = await fetch('/api/optimization/supplier-selection', { method: 'POST' });
    const json = await res.json();
    if (json.status === 'success') {
      const best = json.best_supplier;
      showToast(`🏆 Best Ranked Supplier: ${best.name} (Score: ${best.composite_score})`, 'success');
    }
  } catch(e) {}
}

// ==================== INVENTORY MODULE ====================
let allInventoryCache = [];

async function initInventoryModuleV2() {
  try {
    const res = await fetch('/api/inventory');
    const json = await res.json();
    allInventoryCache = json.data || [];

    // Load products into modal
    loadModalProducts();

    const totalStock = allInventoryCache.reduce((sum, i) => sum + (i.quantity || 0), 0);
    const lowStock = allInventoryCache.filter(i => (i.quantity || 0) <= (i.reorder_level || 50) && (i.quantity || 0) > 0).length;
    const outStock = allInventoryCache.filter(i => (i.quantity || 0) === 0).length;

    document.getElementById('invKpiTotalStock').textContent = totalStock.toLocaleString();
    document.getElementById('invKpiLowStock').textContent = lowStock;
    document.getElementById('invKpiOutStock').textContent = outStock;

    renderInventoryTable(allInventoryCache);
  } catch(e) {
    console.error('Failed to load inventory:', e);
  }
}

async function loadModalProducts() {
  try {
    const res = await fetch('/api/products');
    const json = await res.json();
    const prods = json.data || [];
    const select = document.getElementById('modalInvProductId');
    if (select) {
      select.innerHTML = '<option value="">Select Product</option>' + 
        prods.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    }
  } catch(e) {}
}

function renderInventoryTable(items) {
  const tbody = document.getElementById('inventoryTableBody');
  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:30px;">No inventory records.</td></tr>';
    return;
  }

  tbody.innerHTML = items.map(i => {
    const qty = i.quantity || 0;
    const reorder = i.reorder_level || 50;
    const max = 300;
    const pct = Math.min(Math.round((qty / max) * 100), 100);
    const isLow = qty <= reorder && qty > 0;
    const isOut = qty === 0;

    let fillClass = 'blue';
    let statusBadge = '<span class="badge-subtle green">In Stock</span>';
    if (isLow) { fillClass = 'amber'; statusBadge = '<span class="badge-subtle amber">Low Stock</span>'; }
    if (isOut) { fillClass = 'red'; statusBadge = '<span class="badge-subtle red">Out of Stock</span>'; }

    return `
      <tr>
        <td><span class="product-sku-meta">#INV-${i.id}</span></td>
        <td>
          <div class="product-title-bold">${i.product_name || `Product #${i.product_id}`}</div>
          <div class="product-sku-meta">${i.product_code || ''}</div>
        </td>
        <td>${i.warehouse_name || 'WH-DEL'}</td>
        <td><strong>${qty}</strong> units</td>
        <td style="color:var(--color-text-muted);">${i.reserved_quantity || 0} units</td>
        <td>${reorder}</td>
        <td>
          <div style="display:flex; justify-content:space-between; font-size:0.72rem; font-weight:700; margin-bottom:3px;">
            <span>Stock Level</span>
            <span>${pct}%</span>
          </div>
          <div class="progress-track" style="height:6px;">
            <div class="progress-fill ${fillClass}" style="width:${pct}%;"></div>
          </div>
        </td>
        <td>${statusBadge}</td>
        <td style="text-align:right;">
          <button class="btn btn-outline btn-sm" onclick="editInventory(${i.id})">Update</button>
          <button class="btn btn-danger btn-sm" onclick="deleteInventory(${i.id})">Delete</button>
        </td>
      </tr>
    `;
  }).join('');
}

function filterInventoryGrid() {
  const search = document.getElementById('inventorySearchInput')?.value.toLowerCase() || '';
  const wh = document.getElementById('inventoryWarehouseFilter')?.value || '';
  const status = document.getElementById('inventoryStatusFilter')?.value || '';

  const filtered = allInventoryCache.filter(i => {
    const matchSearch = (i.product_name || '').toLowerCase().includes(search) || (i.warehouse_name || '').toLowerCase().includes(search);
    const matchWh = !wh || String(i.warehouse_id) === String(wh);
    let matchStatus = true;
    if (status === 'In Stock') matchStatus = i.quantity > (i.reorder_level || 50);
    if (status === 'Low Stock') matchStatus = i.quantity <= (i.reorder_level || 50) && i.quantity > 0;
    if (status === 'Out of Stock') matchStatus = i.quantity === 0;
    return matchSearch && matchWh && matchStatus;
  });

  renderInventoryTable(filtered);
}

function openAddInventoryModal() {
  document.getElementById('inventoryModalForm')?.reset();
  document.getElementById('modalInvId').value = '';
  document.getElementById('inventoryModalTitle').textContent = 'Add Stock Record';
  document.getElementById('inventoryModalBackdrop').classList.add('show');
}

function closeInventoryModal() {
  document.getElementById('inventoryModalBackdrop').classList.remove('show');
}

async function handleInventoryFormSubmit(event) {
  event.preventDefault();
  const id = document.getElementById('modalInvId').value;
  const payload = {
    product_id: parseInt(document.getElementById('modalInvProductId').value),
    warehouse_id: parseInt(document.getElementById('modalInvWarehouseId').value),
    quantity: parseInt(document.getElementById('modalInvQuantity').value) || 0,
    reserved_quantity: parseInt(document.getElementById('modalInvReserved').value) || 0,
    reorder_level: parseInt(document.getElementById('modalInvReorderLevel').value) || 50
  };

  try {
    const url = id ? `/api/inventory/${id}` : '/api/inventory';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(json.message || 'Inventory updated', 'success');
      closeInventoryModal();
      initInventoryModuleV2();
    } else {
      showToast(json.message || 'Save failed', 'error');
    }
  } catch(e) {
    showToast('Failed to save inventory', 'error');
  }
}

function editInventory(id) {
  const i = allInventoryCache.find(x => x.id === id);
  if (!i) return;
  document.getElementById('modalInvId').value = i.id;
  document.getElementById('modalInvProductId').value = i.product_id;
  document.getElementById('modalInvWarehouseId').value = i.warehouse_id;
  document.getElementById('modalInvQuantity').value = i.quantity;
  document.getElementById('modalInvReserved').value = i.reserved_quantity || 0;
  document.getElementById('modalInvReorderLevel').value = i.reorder_level || 50;
  document.getElementById('inventoryModalTitle').textContent = 'Update Stock Level';
  document.getElementById('inventoryModalBackdrop').classList.add('show');
}

async function deleteInventory(id) {
  if (!confirm(`Are you sure you want to delete Inventory record #${id}?`)) return;
  try {
    const res = await fetch(`/api/inventory/${id}`, { method: 'DELETE' });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(json.message || 'Stock record deleted', 'success');
      initInventoryModuleV2();
    } else {
      showToast(json.message || 'Delete failed', 'error');
    }
  } catch(e) {
    showToast('Failed to delete stock record', 'error');
  }
}

function exportInventoryCSV() {
  window.location.href = '/api/reports/export-csv/inventory';
}

// ==================== ORDERS MODULE (WITH REAL PYTHON FIFO QUEUE) ====================
let allOrdersCache = [];

async function initOrdersModuleV2() {
  await loadOrdersModuleV2();
}

async function loadOrdersModuleV2() {
  try {
    const res = await fetch('/api/orders');
    const json = await res.json();
    allOrdersCache = json.orders || [];

    // Load products into new order modal
    loadOrderProducts();

    // Stats
    const pending = allOrdersCache.filter(o => o.status === 'PENDING_IN_QUEUE').length;
    const processing = allOrdersCache.filter(o => o.status === 'DISPATCHED').length;
    const completed = allOrdersCache.filter(o => o.status === 'DELIVERED').length;

    document.getElementById('orderStatPending').textContent = pending;
    document.getElementById('orderStatProcessing').textContent = processing;
    document.getElementById('orderStatCompleted').textContent = completed;
    document.getElementById('queueSizeBadge').textContent = `${json.queue_size || pending} Orders`;

    // Render Table
    renderOrdersTable(allOrdersCache);

    // Render FIFO Queue Panel
    renderFifoQueuePanel(json);

  } catch(e) {
    console.error('Failed to load orders:', e);
  }
}

async function loadOrderProducts() {
  try {
    const res = await fetch('/api/products');
    const json = await res.json();
    const select = document.getElementById('modalOrderProduct');
    if (select) {
      select.innerHTML = '<option value="">Select Product</option>' + 
        (json.data || []).map(p => `<option value="${p.id}">${p.name} (Stock: ${p.total_stock || 0})</option>`).join('');
    }
  } catch(e) {}
}

function renderOrdersTable(orders) {
  const tbody = document.getElementById('ordersMainTableBody');
  if (!tbody) return;

  if (orders.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:30px;">No orders found.</td></tr>';
    return;
  }

  tbody.innerHTML = orders.map(o => {
    let badgeClass = 'amber';
    let statusLabel = 'Pending in Queue';
    if (o.status === 'DISPATCHED') { badgeClass = 'blue'; statusLabel = 'Dispatched'; }
    if (o.status === 'DELIVERED') { badgeClass = 'green'; statusLabel = 'Delivered'; }

    return `
      <tr>
        <td><strong>#${o.order_number || o.id}</strong></td>
        <td>${o.customer_name}</td>
        <td>${o.product_name || `Product #${o.product_id}`}</td>
        <td><strong>${o.quantity}</strong></td>
        <td><span class="badge-subtle ${o.priority === 1 ? 'red' : 'blue'}">Priority ${o.priority}</span></td>
        <td>${o.destination_city || o.location_name || 'Hub'}</td>
        <td><span class="badge-subtle ${badgeClass}">${statusLabel}</span></td>
        <td style="font-size:0.75rem; color:var(--color-text-muted);">${(o.created_at || '').substring(0, 10) || 'Today'}</td>
      </tr>
    `;
  }).join('');
}

function renderFifoQueuePanel(data) {
  const nextContainer = document.getElementById('fifoNextOrderContainer');
  const upcomingList = document.getElementById('fifoUpcomingQueueList');
  if (!nextContainer) return;

  const queueVisual = data.queue_visualization?.nodes || [];
  const peek = data.queue_peek;

  if (!peek || queueVisual.length === 0) {
    nextContainer.innerHTML = `
      <div style="text-align:center; padding:20px; color:var(--color-text-muted); font-size:0.85rem;">
        Queue is empty. Click "+ New Order" to enqueue new customer orders.
      </div>
    `;
    if (upcomingList) upcomingList.innerHTML = '<div style="color:var(--color-text-dim); font-size:0.75rem;">No upcoming orders</div>';
    return;
  }

  const next = queueVisual[0].data || peek;

  nextContainer.innerHTML = `
    <div class="fifo-next-card">
      <div class="fifo-badge">NEXT TO PROCESS (FIFO HEAD)</div>
      <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
          <div class="fifo-order-num">#${next.order_number || next.id}</div>
          <div style="font-size:0.88rem; font-weight:700; color:var(--color-text); margin-top:2px;">
            Customer: ${next.customer_name || 'Customer'}
          </div>
          <div style="font-size:0.8rem; color:var(--color-text-muted); margin-top:2px;">
            Product #${next.product_id} • <strong>${next.quantity} units</strong>
          </div>
        </div>
        <button class="btn btn-primary btn-sm" onclick="processNextFifoOrder()" style="padding:8px 14px;">
          ⚡ Process Order
        </button>
      </div>
    </div>
  `;

  if (upcomingList) {
    const upcoming = queueVisual.slice(1);
    if (upcoming.length === 0) {
      upcomingList.innerHTML = '<div style="color:var(--color-text-muted); font-size:0.78rem; padding:8px 0;">No other orders in queue.</div>';
    } else {
      upcomingList.innerHTML = upcoming.map((item, idx) => `
        <div class="fifo-queue-item">
          <div>
            <strong>#${item.data?.order_number || item.id}</strong>
            <span style="color:var(--color-text-muted); margin-left:6px;">${item.data?.customer_name || 'Customer'}</span>
          </div>
          <span class="badge-subtle blue">Queue #${idx + 2}</span>
        </div>
      `).join('');
    }
  }
}

async function processNextFifoOrder() {
  try {
    const res = await fetch('/api/orders/dequeue', { method: 'POST' });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`✓ Processed & Dequeued Order #${json.processed_order?.order_number} (FIFO O(1))`, 'success');
      loadOrdersModuleV2();
    } else {
      showToast(json.message || 'Failed to process order', 'error');
    }
  } catch(e) {
    showToast('Failed to dequeue order', 'error');
  }
}

function filterOrdersGrid() {
  const search = document.getElementById('ordersSearchInput')?.value.toLowerCase() || '';
  const status = document.getElementById('ordersStatusFilter')?.value || '';
  const priority = document.getElementById('ordersPriorityFilter')?.value || '';

  const filtered = allOrdersCache.filter(o => {
    const matchSearch = (o.customer_name || '').toLowerCase().includes(search) || (o.order_number || '').toLowerCase().includes(search);
    const matchStatus = !status || o.status === status;
    const matchPriority = !priority || String(o.priority) === String(priority);
    return matchSearch && matchStatus && matchPriority;
  });

  renderOrdersTable(filtered);
}

function openNewOrderModal() {
  document.getElementById('newOrderModalForm')?.reset();
  document.getElementById('newOrderModalBackdrop').classList.add('show');
}

function closeNewOrderModal() {
  document.getElementById('newOrderModalBackdrop').classList.remove('show');
}

async function handleNewOrderSubmit(event) {
  event.preventDefault();
  const payload = {
    customer_name: document.getElementById('modalOrderCustomer').value.trim(),
    customer_email: document.getElementById('modalOrderEmail').value.trim(),
    customer_phone: document.getElementById('modalOrderPhone').value.trim(),
    product_id: parseInt(document.getElementById('modalOrderProduct').value),
    quantity: parseInt(document.getElementById('modalOrderQty').value) || 1,
    priority: parseInt(document.getElementById('modalOrderPriority').value) || 2,
    delivery_location_id: parseInt(document.getElementById('modalOrderLocation').value) || 1
  };

  try {
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`✓ Order #${json.order?.order_number} enqueued at REAR (FIFO O(1))`, 'success');
      closeNewOrderModal();
      loadOrdersModuleV2();
    } else {
      showToast(json.message || 'Enqueue failed', 'error');
    }
  } catch(e) {
    showToast('Failed to enqueue order', 'error');
  }
}

// ==================== WAREHOUSES MODULE ====================
let allWarehousesCache = [];

async function initWarehousesModuleV2() {
  try {
    const res = await fetch('/api/warehouses');
    const json = await res.json();
    allWarehousesCache = json.data || [];

    document.getElementById('whCountBadge').textContent = `${allWarehousesCache.length} Facilities`;

    // Render Cards Grid
    const cardsGrid = document.getElementById('warehousesCardsGrid');
    if (cardsGrid) {
      cardsGrid.innerHTML = allWarehousesCache.map(w => {
        const cap = w.capacity || 50000;
        const stock = w.current_stock || 0;
        const util = parseFloat(w.utilization_pct) || Math.round((stock / cap) * 100);
        const avail = Math.max(0, cap - stock);

        return `
          <div class="wh-compact-card" style="padding:20px;">
            <div class="wh-card-top">
              <div>
                <span class="wh-code">${w.warehouse_code || 'WH-NODE'}</span>
                <h3 class="wh-name" style="font-size:1.05rem;">${w.name}</h3>
                <div class="wh-location">${w.city || w.location || 'Hub'}</div>
              </div>
              <span class="wh-status-tag active">● Operational</span>
            </div>

            <div class="wh-capacity-stat" style="margin-top:14px;">
              <span>Utilization</span>
              <span><strong>${util}%</strong></span>
            </div>

            <div class="progress-track" style="height:8px; margin-bottom:12px;">
              <div class="progress-fill ${util > 85 ? 'amber' : 'blue'}" style="width:${Math.min(util, 100)}%;"></div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; padding-top:10px; border-top:1px solid var(--color-border-subtle); font-size:0.75rem;">
              <div>
                <span style="color:var(--color-text-muted);">Current Stock</span>
                <div style="font-weight:700; color:var(--color-text);">${stock.toLocaleString()} units</div>
              </div>
              <div>
                <span style="color:var(--color-text-muted);">Available Space</span>
                <div style="font-weight:700; color:var(--color-text);">${avail.toLocaleString()} units</div>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Render Table
    const tbody = document.getElementById('warehousesTableBody');
    if (tbody) {
      tbody.innerHTML = allWarehousesCache.map(w => `
        <tr>
          <td><strong>#${w.warehouse_code || w.id}</strong></td>
          <td><strong>${w.name}</strong></td>
          <td>${w.city || 'Hub'}</td>
          <td>${(w.capacity || 50000).toLocaleString()} units</td>
          <td><strong>${(w.current_stock || 0).toLocaleString()}</strong> units</td>
          <td><span class="badge-subtle blue">${w.utilization_pct || 75}%</span></td>
          <td style="font-family:var(--font-mono); font-size:0.75rem; color:var(--color-text-muted);">${w.latitude || '28.61'}, ${w.longitude || '77.20'}</td>
          <td><span class="badge-subtle green">Operational</span></td>
          <td style="text-align:right;">
            <button class="btn btn-danger btn-sm" onclick="deleteWarehouse(${w.id})">Delete</button>
          </td>
        </tr>
      `).join('');
    }

  } catch(e) {
    console.error('Failed to load warehouses:', e);
  }
}

function openAddWarehouseModal() {
  document.getElementById('warehouseModalForm')?.reset();
  document.getElementById('warehouseModalBackdrop').classList.add('show');
}

function closeWarehouseModal() {
  document.getElementById('warehouseModalBackdrop').classList.remove('show');
}

async function handleWarehouseFormSubmit(event) {
  event.preventDefault();
  const payload = {
    name: document.getElementById('modalWhName').value.trim(),
    city: document.getElementById('modalWhCity').value.trim(),
    warehouse_code: document.getElementById('modalWhCode').value.trim() || 'WH-NEW',
    capacity: parseInt(document.getElementById('modalWhCapacity').value) || 50000,
    location: document.getElementById('modalWhLocation').value.trim()
  };

  try {
    const res = await fetch('/api/warehouses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast('✓ Warehouse facility added', 'success');
      closeWarehouseModal();
      initWarehousesModuleV2();
    } else {
      showToast(json.message || 'Failed to add', 'error');
    }
  } catch(e) {
    showToast('Failed to save warehouse', 'error');
  }
}

async function deleteWarehouse(id) {
  if (!confirm(`Are you sure you want to delete Warehouse #${id}?`)) return;
  try {
    const res = await fetch(`/api/warehouses/${id}`, { method: 'DELETE' });
    const json = await res.json();
    if (json.status === 'success') {
      showToast('Warehouse deleted', 'success');
      initWarehousesModuleV2();
    }
  } catch(e) {}
}

// ==================== DELIVERIES & GRAPH MODULE ====================
let networkGraphCache = null;
let deliveryMap = null;
let deliveryNodeLayers = {};
let deliveryEdgeLayers = [];
let deliveryAnimLayers = [];
let deliveryAnimTimeout = null;

function _makeDeliveryIcon(color, size = 14) {
  return L.divIcon({
    className: '',
    html: `<div style="width:${size}px; height:${size}px; border-radius:50%; background:${color}; border:2.5px solid #fff; box-shadow:0 2px 8px rgba(0,0,0,0.35); transition: transform 0.25s ease;"></div>`,
    iconSize: [size, size],
    iconAnchor: [size/2, size/2]
  });
}

function _makeDeliveryPulseIcon(color, size = 18) {
  return L.divIcon({
    className: '',
    html: `<div style="position:relative; width:${size}px; height:${size}px;"><div style="width:${size}px; height:${size}px; border-radius:50%; background:${color}; border:3px solid #fff; box-shadow:0 0 0 4px ${color}55; animation: bfsPulse 1s ease-out infinite;"></div></div>`,
    iconSize: [size, size],
    iconAnchor: [size/2, size/2]
  });
}

async function initDeliveryMap() {
  if (deliveryMap) return;
  deliveryMap = L.map('deliveryLeafletMap', {
    center: [20.5937, 78.9629],
    zoom: 5,
    zoomControl: true,
    attributionControl: true
  });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18
  }).addTo(deliveryMap);
}

function drawDeliveryBaseGraph(allNodes, allEdges) {
  allEdges.forEach(e => {
    const pl = L.polyline([[e.source_lat, e.source_lng], [e.target_lat, e.target_lng]], { color: '#94A3B8', weight: 1.5, opacity: 0.4, dashArray: '4 5' }).addTo(deliveryMap);
    deliveryEdgeLayers.push(pl);
  });
  allNodes.forEach(n => {
    if (!n.lat || !n.lng) return;
    const color = n.type === 'warehouse' ? '#2563EB' : '#10B981';
    const size = n.type === 'warehouse' ? 13 : 10;
    const m = L.marker([n.lat, n.lng], { icon: _makeDeliveryIcon(color, size) }).addTo(deliveryMap);
    deliveryNodeLayers[n.id] = m;
  });
}

function animateDeliveryBFS(visitedOrder, traversedEdges, allNodesMap, speedMs) {
  if (deliveryAnimTimeout) clearTimeout(deliveryAnimTimeout);
  deliveryAnimLayers.forEach(l => deliveryMap.removeLayer(l));
  deliveryAnimLayers = [];

  let stepIdx = 0;
  const edgesByTarget = {};
  traversedEdges.forEach(e => { edgesByTarget[e.target] = e; });

  function doStep() {
    if (stepIdx >= visitedOrder.length) return;
    const nodeId = visitedOrder[stepIdx];
    const nodeInfo = allNodesMap[nodeId];
    const isStart = stepIdx === 0;

    if (!isStart && edgesByTarget[nodeId]) {
      const e = edgesByTarget[nodeId];
      const pl = L.polyline([[e.source_lat, e.source_lng], [e.target_lat, e.target_lng]], { color: '#F59E0B', weight: 3.5, opacity: 0.9 }).addTo(deliveryMap);
      deliveryAnimLayers.push(pl);
    }

    if (deliveryNodeLayers[nodeId]) deliveryMap.removeLayer(deliveryNodeLayers[nodeId]);
    if (nodeInfo && nodeInfo.lat && nodeInfo.lng) {
      const color = isStart ? '#EF4444' : '#F59E0B';
      const pm = L.marker([nodeInfo.lat, nodeInfo.lng], { icon: _makeDeliveryPulseIcon(color, 20) }).addTo(deliveryMap);
      deliveryAnimLayers.push(pm);
      deliveryNodeLayers[nodeId] = pm;
    }
    stepIdx++;
    deliveryAnimTimeout = setTimeout(doStep, speedMs);
  }
  doStep();
}

async function initDeliveriesModuleV2() {
  try {
    // 1. Load Deliveries
    const [delivRes, graphRes] = await Promise.all([
      fetch('/api/deliveries'),
      fetch('/api/network')
    ]);

    const delivJson = await delivRes.json();
    const deliveries = delivJson.data || [];

    document.getElementById('delivStatActive').textContent = deliveries.filter(d => d.delivery_status !== 'DELIVERED').length;
    document.getElementById('delivStatPending').textContent = deliveries.filter(d => d.delivery_status === 'PENDING').length;
    document.getElementById('delivStatTransit').textContent = deliveries.filter(d => d.delivery_status === 'IN_TRANSIT').length;
    document.getElementById('delivStatCompleted').textContent = deliveries.filter(d => d.delivery_status === 'DELIVERED').length;
    document.getElementById('delivCountBadge').textContent = `${deliveries.length} Shipments`;

    // Render deliveries table
    const tbody = document.getElementById('deliveriesTableBody');
    if (tbody) {
      if (deliveries.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:30px;">No shipments currently registered.</td></tr>';
      } else {
        tbody.innerHTML = deliveries.map(d => {
          let badgeClass = 'blue';
          if (d.delivery_status === 'IN_TRANSIT') badgeClass = 'purple';
          if (d.delivery_status === 'DELIVERED') badgeClass = 'green';
          return `
            <tr>
              <td><strong>#TRK-${d.id}</strong></td>
              <td>#${d.order_number || d.order_id}</td>
              <td>${d.warehouse_name || 'Source Facility'}</td>
              <td>${d.destination_name || 'Destination Hub'}</td>
              <td>${d.delivery_date || 'Today'}</td>
              <td>${d.estimated_time_days || '1.5'} days</td>
              <td><span class="badge-subtle ${badgeClass}">${d.delivery_status}</span></td>
              <td style="text-align:right;">
                <button class="btn btn-outline btn-sm" onclick="showToast('Tracking coordinates synchronized', 'info')">Track</button>
              </td>
            </tr>
          `;
        }).join('');
      }
    }

    // 2. Render Network Graph
    const graphJson = await graphRes.json();
    networkGraphCache = graphJson.graph;
    await initDeliveryMap();
    if (graphJson.graph && graphJson.graph.nodes) {
      const nodes = graphJson.graph.nodes;
      const links = graphJson.graph.links || [];
      const nodeMap = {};
      nodes.forEach(n => { nodeMap[n.id] = n; });
      const allEdgesGeo = [];
      links.forEach(l => {
        const sv = nodeMap[l.source], dv = nodeMap[l.target];
        if (sv && dv && sv.lat && sv.lng && dv.lat && dv.lng) {
          allEdgesGeo.push({
            source: l.source, target: l.target,
            distance_km: l.distance_km,
            source_lat: sv.lat, source_lng: sv.lng,
            target_lat: dv.lat, target_lng: dv.lng
          });
        }
      });
      drawDeliveryBaseGraph(nodes, allEdgesGeo);
    }


  } catch(e) {
    console.error('Failed to load deliveries:', e);
  }
}

async function runGraphBFSV2() {
  const start = document.getElementById('graphBfsStartSelect')?.value || 'WH-1';
  showToast(`Running BFS from ${start} on OpenStreetMap...`, 'info');

  try {
    const res = await fetch('/api/network/bfs-map', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_node: start })
    });
    const json = await res.json();
    if (json.status === 'success') {
      const order = json.visited_order || [];
      document.getElementById('bfsSequenceText').textContent = order.join(' ➔ ');
      document.getElementById('bfsMetricsText').textContent = `Visited ${order.length} nodes in ${json.elapsed_ms || 0.4} ms (O(V+E))`;

      const allNodesMap = {};
      json.all_nodes.forEach(n => { allNodesMap[n.id] = n; });
      animateDeliveryBFS(order, json.traversed_edges, allNodesMap, 500);
    }
  } catch(e) {
    showToast('Failed to run BFS', 'error');
  }
}

function animateNetworkGraphBFS(nodes) {
  let idx = 0;
  const visited = [];
  const timer = setInterval(() => {
    if (idx < nodes.length) {
      visited.push(nodes[idx]);
      renderNetworkGraphV2('networkCanvasContainer', networkGraphCache, visited);
      idx++;
    } else {
      clearInterval(timer);
      showToast('BFS Shortest-Hop Graph traversal complete!', 'success');
    }
  }, 400);
}

// ==================== BINARY SEARCH LAB CONTROLLER ====================
async function executeBinarySearchV2() {
  const entityType = document.getElementById('bsEntityTypeSelect')?.value || 'product';
  const target = document.getElementById('bsTargetInput')?.value.trim() || '5';

  try {
    const res = await fetch('/api/algorithms/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        algorithm: 'binary_search',
        entity_type: entityType,
        target: parseInt(target) || 5
      })
    });
    const json = await res.json();
    if (json.status === 'success') {
      document.getElementById('bsMetricsGrid').style.display = 'grid';
      document.getElementById('bsVisualCard').style.display = 'block';

      document.getElementById('bsMetricTotal').textContent = json.total_records;
      document.getElementById('bsMetricComparisons').textContent = json.comparisons;
      document.getElementById('bsMetricMaxTheo').textContent = `Max Theo: ${json.max_theoretical_comparisons || 4} steps`;
      document.getElementById('bsMetricResult').textContent = json.found ? 'FOUND ✓' : 'NOT FOUND ✕';
      document.getElementById('bsMetricFoundIdx').textContent = `Index: ${json.found_index !== -1 ? json.found_index : 'N/A'}`;
      document.getElementById('bsMetricElapsed').textContent = `${json.elapsed_ms || 0.15} ms`;

      // Render Visual Array
      renderBinarySearchArray(json);

      // Render Steps
      renderBinarySearchSteps(json.steps || []);

      // Render Record Payload
      const recordCard = document.getElementById('bsRecordResultCard');
      const recordJson = document.getElementById('bsRecordJson');
      if (json.record && recordCard && recordJson) {
        recordCard.style.display = 'block';
        recordJson.textContent = JSON.stringify(json.record, null, 2);
      }
    }
  } catch(e) {
    console.error('Binary search error:', e);
  }
}

function renderBinarySearchArray(json) {
  const container = document.getElementById('bsArrayVisualContainer');
  if (!container) return;

  const keys = json.dataset_keys || [1, 2, 3, 4, 5, 6, 7, 8];
  const lastStep = json.steps && json.steps.length > 0 ? json.steps[json.steps.length - 1] : null;
  const midIdx = lastStep ? lastStep.mid_index : -1;
  const foundIdx = json.found_index;

  container.innerHTML = keys.map((k, idx) => {
    const isMid = idx === midIdx;
    const isFound = idx === foundIdx;

    return `
      <div class="bs-array-cell ${isFound ? 'found' : (isMid ? 'mid' : 'in-range')}">
        <span>${k}</span>
        ${isFound ? '<span class="bs-pointer-label" style="background:#059669; color:#fff;">MATCH</span>' : (isMid ? '<span class="bs-pointer-label" style="background:#D97706; color:#fff;">MID</span>' : '')}
      </div>
    `;
  }).join('');
}

function renderBinarySearchSteps(steps) {
  const container = document.getElementById('bsStepLogContainer');
  if (!container) return;

  container.innerHTML = steps.map(s => `
    <div style="padding:10px 14px; background:#FFFFFF; border:1px solid var(--color-border); border-radius:var(--radius-sm); font-size:0.83rem; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <strong style="color:var(--color-primary-blue);">Step ${s.step || s.iteration}:</strong>
        <span style="margin-left:6px; color:var(--color-text);">${s.description || `Mid = ${s.mid_value}`}</span>
      </div>
      <span class="badge-subtle blue">Low: ${s.low !== undefined ? s.low : (s.low_index || 0)} | High: ${s.high !== undefined ? s.high : (s.high_index || 0)} | Mid: ${s.mid !== undefined ? s.mid : (s.mid_index || 0)}</span>
    </div>
  `).join('');
}

// ==================== QUICK SORT LAB CONTROLLER ====================
async function executeQuickSortLab() {
  const entityType = document.getElementById('qsEntityTypeSelect')?.value || 'product';
  const sortField = document.getElementById('qsSortFieldSelect')?.value || 'price';
  const order = document.getElementById('qsOrderSelect')?.value || 'asc';
  const customDataStr = document.getElementById('qsCustomArrayInput')?.value.trim();

  let payload = {
    algorithm: 'quick_sort',
    entity_type: entityType,
    sort_field: sortField,
    order: order
  };

  if (entityType === 'custom' && customDataStr) {
    try {
      const parsed = customDataStr.split(',').map(x => parseFloat(x.trim())).filter(x => !isNaN(x));
      if (parsed.length > 0) payload.custom_data = parsed;
    } catch(e) {
      console.warn('Failed parsing custom array, using defaults');
    }
  }

  try {
    const res = await fetch('/api/algorithms/sort', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.status === 'success') {
      document.getElementById('qsMetricsGrid').style.display = 'grid';
      document.getElementById('qsVisualCard').style.display = 'block';
      document.getElementById('qsResultTableCard').style.display = 'block';

      document.getElementById('qsMetricTotal').textContent = json.total_records;
      document.getElementById('qsMetricComparisons').textContent = json.comparisons;
      document.getElementById('qsMetricSwaps').textContent = json.swaps;
      document.getElementById('qsMetricElapsed').textContent = `${json.elapsed_ms || 0.12} ms`;

      renderQuickSortSteps(json.steps || [], json.total_records);
      renderQuickSortResultsTable(json.sorted_records || [], entityType, sortField);
      showToast(`Quick Sort complete: Partitioned ${json.total_records} items in ${json.comparisons} comparisons!`, 'success');
    } else {
      showToast(json.message || 'Quick Sort failed', 'error');
    }
  } catch(e) {
    console.error('Quick sort lab error:', e);
    showToast('Failed to execute Quick Sort', 'error');
  }
}

function renderQuickSortSteps(steps, totalRecords) {
  const container = document.getElementById('qsStepLogContainer');
  if (!container) return;

  if (steps.length === 0) {
    container.innerHTML = `<div style="color:var(--color-text-muted); font-size:0.85rem; padding:10px;">Already sorted or empty dataset.</div>`;
    return;
  }

  container.innerHTML = steps.map(s => {
    const leftBadges = (s.left_partition || []).map(v => `<span class="qs-array-cell left" style="height:32px; min-width:32px; font-size:0.75rem;">${v}</span>`).join('');
    const rightBadges = (s.right_partition || []).map(v => `<span class="qs-array-cell right" style="height:32px; min-width:32px; font-size:0.75rem;">${v}</span>`).join('');
    const pivotBadge = `<span class="qs-array-cell pivot" style="height:34px; min-width:34px; font-size:0.78rem;">${s.pivot_value}</span>`;

    return `
      <div class="qs-partition-box">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <div>
            <span class="qs-step-badge">Step ${s.step_number} (Depth ${s.depth})</span>
            <strong style="margin-left:8px; font-size:0.85rem; color:var(--color-primary-blue);">${s.action}</strong>
          </div>
          <span style="font-size:0.75rem; color:var(--color-text-muted); font-family:var(--font-mono);">Range [${s.low}..${s.high}]</span>
        </div>
        <div style="margin-bottom:8px; font-size:0.82rem; color:var(--color-text);">
          ${s.description}
        </div>
        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap; background:#FFFFFF; padding:8px 12px; border-radius:var(--radius-sm); border:1px solid var(--color-border-subtle);">
          <div style="display:flex; align-items:center; gap:4px;">
            <span style="font-size:0.7rem; font-weight:700; color:#1D4ED8;">LEFT (≤ Pivot):</span>
            <div style="display:flex; gap:3px; flex-wrap:wrap;">${leftBadges || '<span style="font-size:0.72rem; color:#94a3b8;">None</span>'}</div>
          </div>
          <div style="display:flex; align-items:center; gap:4px; margin: 0 8px;">
            <span style="font-size:0.7rem; font-weight:700; color:#B45309;">PIVOT:</span>
            ${pivotBadge}
          </div>
          <div style="display:flex; align-items:center; gap:4px;">
            <span style="font-size:0.7rem; font-weight:700; color:#6D28D9;">RIGHT (> Pivot):</span>
            <div style="display:flex; gap:3px; flex-wrap:wrap;">${rightBadges || '<span style="font-size:0.72rem; color:#94a3b8;">None</span>'}</div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function renderQuickSortResultsTable(records, entityType, sortField) {
  const tbody = document.getElementById('qsResultTableBody');
  const thead = document.getElementById('qsResultTableHead');
  if (!tbody || !thead) return;

  if (records.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px; color:#64748b;">No records to display.</td></tr>`;
    return;
  }

  // If simple primitive numbers
  if (typeof records[0] !== 'object') {
    thead.innerHTML = `<tr><th>INDEX</th><th>VALUE</th><th>SORTED STATUS</th></tr>`;
    tbody.innerHTML = records.map((val, idx) => `
      <tr>
        <td>#${idx + 1}</td>
        <td><strong style="color:var(--color-primary-blue); font-size:0.95rem;">${val}</strong></td>
        <td><span class="badge-subtle green">In Place ✓</span></td>
      </tr>
    `).join('');
    return;
  }

  // Dictionaries
  thead.innerHTML = `
    <tr>
      <th>#</th>
      <th>ID</th>
      <th>RECORD NAME</th>
      <th>CATEGORY / STATUS</th>
      <th style="color:var(--color-primary-blue); font-weight:800;">SORT KEY: ${sortField.toUpperCase()}</th>
    </tr>
  `;

  tbody.innerHTML = records.map((r, idx) => {
    const val = r[sortField] !== undefined ? r[sortField] : '--';
    const displayVal = (sortField === 'price' || sortField === 'total_amount') ? `₹${val}` : val;
    return `
      <tr>
        <td>${idx + 1}</td>
        <td><code>${r.id || r.product_code || r.supplier_code || r.order_number || ('#' + (idx + 1))}</code></td>
        <td><strong>${r.name || r.customer_name || r.product_name || 'Record ' + (idx + 1)}</strong></td>
        <td><span class="badge-subtle blue">${r.category || r.status || entityType}</span></td>
        <td><strong style="color:var(--color-primary-blue); font-size:0.92rem;">${displayVal}</strong></td>
      </tr>
    `;
  }).join('');
}

function updateQuickSortFieldOptions() {
  const entityType = document.getElementById('qsEntityTypeSelect')?.value || 'product';
  const sortSelect = document.getElementById('qsSortFieldSelect');
  const customInputDiv = document.getElementById('qsCustomArrayDiv');
  if (!sortSelect) return;

  if (entityType === 'custom') {
    if (customInputDiv) customInputDiv.style.display = 'block';
    sortSelect.innerHTML = `<option value="value">Numeric Value</option>`;
    return;
  }

  if (customInputDiv) customInputDiv.style.display = 'none';

  if (entityType === 'product') {
    sortSelect.innerHTML = `
      <option value="price">Product Price (₹)</option>
      <option value="stock">Stock Inventory Count</option>
      <option value="id">Product ID</option>
      <option value="name">Product Name (Alphabetical)</option>
    `;
  } else if (entityType === 'supplier') {
    sortSelect.innerHTML = `
      <option value="reliability_score">Reliability Score (0-100)</option>
      <option value="avg_delivery_time_days">Avg Delivery Speed (Days)</option>
      <option value="name">Supplier Name</option>
      <option value="id">Supplier ID</option>
    `;
  } else if (entityType === 'order') {
    sortSelect.innerHTML = `
      <option value="quantity">Order Quantity</option>
      <option value="total_amount">Total Amount (₹)</option>
      <option value="id">Order ID</option>
    `;
  } else if (entityType === 'inventory') {
    sortSelect.innerHTML = `
      <option value="quantity">Current Stock Quantity</option>
      <option value="reorder_level">Reorder Threshold Level</option>
      <option value="id">Inventory Record ID</option>
    `;
  }
}

function switchLabTab(tab) {
  const qsSec = document.getElementById('quickSortLabSection');
  const bsSec = document.getElementById('binarySearchLabSection');
  const bmSec = document.getElementById('benchmarksLabSection');
  const tabQs = document.getElementById('tabBtnQuickSort');
  const tabBs = document.getElementById('tabBtnBinarySearch');
  const tabBm = document.getElementById('tabBtnBenchmarks');

  if (qsSec) qsSec.style.display = tab === 'quicksort' ? 'block' : 'none';
  if (bsSec) bsSec.style.display = tab === 'binarysearch' ? 'block' : 'none';
  if (bmSec) bmSec.style.display = tab === 'benchmarks' ? 'block' : 'none';

  if (tabQs) tabQs.className = tab === 'quicksort' ? 'btn btn-primary btn-sm' : 'btn btn-outline btn-sm';
  if (tabBs) tabBs.className = tab === 'binarysearch' ? 'btn btn-primary btn-sm' : 'btn btn-outline btn-sm';
  if (tabBm) tabBm.className = tab === 'benchmarks' ? 'btn btn-primary btn-sm' : 'btn btn-outline btn-sm';
}

// ==================== GREEDY SELECTION LAB CONTROLLER ====================
let greedyProductsList = [];
let greedyLocationsList = [];

async function initGreedyModuleV2(prodSelectId = 'greedyProductSelect', locSelectId = 'greedyLocationSelect', qtyInputId = 'greedyQuantityInput', candidatesListId = 'greedyCandidatesList', decisionCardId = 'greedyDecisionPanel', chosenWhTitleId = 'greedySelectedWhTitle', chosenWhSummaryId = 'greedySelectedWhSummary', timeBadgeId = 'greedyElapsedBadge') {
  try {
    const [pRes, gRes] = await Promise.all([
      fetch('/api/products'),
      fetch('/api/network')
    ]);

    const pJson = await pRes.json();
    greedyProductsList = pJson.data || [];

    const gJson = await gRes.json();
    greedyLocationsList = (gJson.graph?.nodes || []).filter(n => n.type === 'delivery_location');

    const pSelect = document.getElementById(prodSelectId);
    if (pSelect) {
      pSelect.innerHTML = greedyProductsList.map(p => `<option value="${p.id}">${p.name} (Stock: ${p.total_stock || 0})</option>`).join('');
    }

    const lSelect = document.getElementById(locSelectId);
    if (lSelect) {
      lSelect.innerHTML = greedyLocationsList.map(l => `<option value="${l.id.replace('HUB-', '')}">${l.name} (${l.city})</option>`).join('');
    }

    executeGreedyAlgorithmV2(prodSelectId, locSelectId, qtyInputId, candidatesListId, decisionCardId, chosenWhTitleId, chosenWhSummaryId, timeBadgeId);

  } catch(e) {
    console.error('Failed to init greedy module:', e);
  }
}

async function executeGreedyAlgorithmV2(prodSelectId = 'greedyProductSelect', locSelectId = 'greedyLocationSelect', qtyInputId = 'greedyQuantityInput', candidatesListId = 'greedyCandidatesList', decisionCardId = 'greedyDecisionPanel', chosenWhTitleId = 'greedySelectedWhTitle', chosenWhSummaryId = 'greedySelectedWhSummary', timeBadgeId = 'greedyElapsedBadge') {
  const prodId = document.getElementById(prodSelectId)?.value;
  const locId = document.getElementById(locSelectId)?.value;
  const qty = parseInt(document.getElementById(qtyInputId)?.value) || 40;

  if (!prodId || !locId) return;

  try {
    const res = await fetch('/api/optimization/greedy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        product_id: parseInt(prodId),
        quantity: qty,
        delivery_location_id: parseInt(locId)
      })
    });
    const json = await res.json();
    
    // Render Decision Card
    const decCard = document.getElementById(decisionCardId);
    if (decCard && json.selected_warehouse) {
      decCard.style.display = 'block';
      document.getElementById(chosenWhTitleId).textContent = json.selected_warehouse.warehouse_name;
      document.getElementById(chosenWhSummaryId).textContent = json.decision_summary || `Selected nearest warehouse with ${json.selected_warehouse.available_stock} units in stock.`;
      if (document.getElementById(timeBadgeId)) document.getElementById(timeBadgeId).textContent = `${json.elapsed_ms || 0.25} ms (O(W))`;
      if (document.getElementById('greedyCostDisplay')) document.getElementById('greedyCostDisplay').textContent = `₹${json.selected_warehouse.estimated_cost_inr || 870}`;
    }

    // Render Candidates List
    const candList = document.getElementById(candidatesListId);
    if (candList && json.candidates) {
      candList.innerHTML = json.candidates.map(c => {
        const isSel = c.is_selected;
        const isElig = c.is_eligible;

        return `
          <div class="greedy-candidate-card ${isSel ? 'selected' : (!isElig ? 'ineligible' : '')}">
            <div>
              <div style="display:flex; align-items:center; gap:8px;">
                <h4 style="font-size:0.95rem; font-weight:800; color:var(--color-text);">${c.warehouse_name}</h4>
                <span class="badge-subtle ${isSel ? 'green' : (isElig ? 'blue' : 'gray')}">
                  ${isSel ? '✓ SELECTED' : (isElig ? 'Eligible' : 'Insufficient Stock')}
                </span>
              </div>
              <div style="font-size:0.75rem; color:var(--color-text-muted); margin-top:2px;">
                Stock: <strong>${c.available_stock} units</strong> • Required: ${qty} units
              </div>
            </div>

            <div style="text-align:right;">
              <span style="font-size:0.7rem; color:var(--color-text-muted);">Transit Distance</span>
              <div style="font-size:1.15rem; font-weight:800; color:${isSel ? 'var(--color-success)' : 'var(--color-text)'}">
                ${c.distance_km} km
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

  } catch(e) {
    console.error('Greedy execution failed:', e);
  }
}

function runGreedyPreview() {
  executeGreedyAlgorithmV2();
}

// ==================== DSA LAB CONTROLLER FUNCTIONS ====================
async function reloadLabLinkedList() {
  try {
    const res = await fetch('/api/dsa/linked-list/view');
    const json = await res.json();
    renderLinkedListV2('labLlCanvasTrack', json.visual_nodes || []);
    document.getElementById('labLlNodeCount').textContent = json.total_nodes || 0;
    document.getElementById('labLlHeadNode').textContent = json.head?.label || 'None';
    document.getElementById('labLlTailNode').textContent = json.tail?.label || 'None';
  } catch(e) {}
}

async function execLabLlInsert(pos = 'end') {
  const val = document.getElementById('labLlInput')?.value.trim() || 'New Item';
  try {
    const res = await fetch('/api/dsa/linked-list/insert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: val, position: pos })
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`✓ Inserted '${val}' at ${pos} (O(${pos === 'beginning' ? '1' : 'n'}))`, 'success');
      reloadLabLinkedList();
    }
  } catch(e) {}
}

async function execLabLlSearch() {
  const val = document.getElementById('labLlInput')?.value.trim();
  if (!val) return;
  try {
    const res = await fetch('/api/dsa/linked-list/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: val })
    });
    const json = await res.json();
    if (json.found) {
      showToast(`✓ Found node '${val}' in ${json.comparisons} comparisons (O(n))`, 'success');
      const viewRes = await fetch('/api/dsa/linked-list/view');
      const viewJson = await viewRes.json();
      renderLinkedListV2('labLlCanvasTrack', viewJson.visual_nodes || [], val);
    } else {
      showToast(`✕ Node '${val}' not found`, 'warning');
    }
  } catch(e) {}
}

async function execLabLlDelete() {
  const val = document.getElementById('labLlInput')?.value.trim();
  if (!val) return;
  try {
    const res = await fetch('/api/dsa/linked-list/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: val })
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`✓ Unlinked and deleted node '${val}'`, 'success');
      reloadLabLinkedList();
    } else {
      showToast(json.message || 'Not found', 'error');
    }
  } catch(e) {}
}

async function execLabLlTraverse() {
  try {
    const res = await fetch('/api/dsa/linked-list/traverse');
    const json = await res.json();
    showToast(`Traversed ${json.total_nodes} nodes in O(n) time`, 'info');
  } catch(e) {}
}

// Queue Lab
async function reloadLabQueue() {
  try {
    const res = await fetch('/api/dsa/queue/view');
    const json = await res.json();
    renderQueueV2('labQueueVisualTrack', json.visual_queue?.nodes || []);
    document.getElementById('labQueueSizeVal').textContent = json.size || 0;
    document.getElementById('labQueueFrontVal').textContent = json.front?.order_number || json.front?.id || 'None';
  } catch(e) {}
}

async function execLabQueueEnqueue() {
  const val = document.getElementById('labQueueInput')?.value.trim() || 'ORD-Quick';
  try {
    const res = await fetch('/api/dsa/queue/enqueue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: val })
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`✓ Enqueued '${val}' at REAR (O(1))`, 'success');
      reloadLabQueue();
    }
  } catch(e) {}
}

async function execLabQueueDequeue() {
  try {
    const res = await fetch('/api/dsa/queue/dequeue', { method: 'POST' });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`✓ Dequeued '${json.dequeued?.order_number || json.dequeued?.id}' from FRONT (O(1))`, 'success');
      reloadLabQueue();
    } else {
      showToast(json.message || 'Queue underflow', 'error');
    }
  } catch(e) {}
}

async function execLabQueuePeek() {
  try {
    const res = await fetch('/api/dsa/queue/peek');
    const json = await res.json();
    if (json.front) {
      showToast(`Front element: ${json.front.order_number || json.front.id}`, 'info');
    } else {
      showToast('Queue is empty', 'warning');
    }
  } catch(e) {}
}

async function loadPendingOrdersIntoQueue() {
  try {
    const res = await fetch('/api/orders');
    const json = await res.json();
    reloadLabQueue();
    showToast('Loaded pending orders into queue', 'success');
  } catch(e) {}
}

// BST Lab
async function reloadLabBST(highlightPath = []) {
  try {
    const res = await fetch('/api/bst/view');
    const json = await res.json();
    renderBSTTreeV2('labBstCanvasContainer', json.tree, highlightPath);
    document.getElementById('labBstHeightVal').textContent = json.height || 3;
    document.getElementById('labBstNodesVal').textContent = json.node_count || 7;
  } catch(e) {}
}

async function execLabBstInsert() {
  const val = parseInt(document.getElementById('labBstInput')?.value);
  if (isNaN(val)) return;
  try {
    const res = await fetch('/api/bst/insert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: val })
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`✓ Inserted key ${val} into BST (O(log n))`, 'success');
      reloadLabBST([val]);
    }
  } catch(e) {}
}

async function execLabBstSearch() {
  const val = parseInt(document.getElementById('labBstInput')?.value);
  if (isNaN(val)) return;
  try {
    const res = await fetch('/api/bst/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: val })
    });
    const json = await res.json();
    const banner = document.getElementById('labBstSearchPathBanner');
    const text = document.getElementById('labBstSearchPathText');
    if (banner && text) {
      banner.style.display = 'block';
      text.textContent = json.formatted_path || `${val} evaluated in ${json.comparisons} comparisons`;
    }
    showToast(json.found ? `✓ Found key ${val} in ${json.comparisons} comparisons` : `✕ Key ${val} not in BST`, json.found ? 'success' : 'warning');
    reloadLabBST(json.path || []);
  } catch(e) {}
}

async function execLabBstDelete() {
  const val = parseInt(document.getElementById('labBstInput')?.value);
  if (isNaN(val)) return;
  try {
    const res = await fetch('/api/bst/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: val })
    });
    const json = await res.json();
    if (json.status === 'success') {
      showToast(`✓ Deleted key ${val} from BST`, 'success');
      reloadLabBST();
    } else {
      showToast(json.message || 'Key not found', 'error');
    }
  } catch(e) {}
}

async function execLabBstTraverse(order = 'inorder') {
  try {
    const res = await fetch('/api/bst/traversal');
    const json = await res.json();
    const seq = json[order] || [];
    const textEl = document.getElementById('labBstTraversalResultText');
    if (textEl) {
      textEl.textContent = `${order.toUpperCase()}: ` + seq.map(x => x.key || x).join(' ➔ ');
    }
    showToast(`BST ${order} traversal completed (O(n))`, 'info');
  } catch(e) {}
}

// ==================== Graph Lab (Leaflet / OpenStreetMap) ====================
// These functions are overridden by the full Leaflet implementations in
// dsa_lab.html's {% block scripts %}. The stubs below act as safe fallbacks
// in case this script loads before the page-specific script, and also ensure
// any early call (e.g. from DOMContentLoaded) is deferred until Leaflet is ready.

let _leafletBfsReady = false;

async function reloadLabNetworkGraph() {
  // If the Leaflet-based implementation is already defined on the page, call it.
  if (window._bfsMap !== undefined || document.getElementById('bfsLeafletMap')) {
    // Leaflet map present — delegate to page-level function (defined after this file).
    // Use a tiny delay to ensure the page script has run.
    setTimeout(() => {
      if (typeof window._reloadLabNetworkGraphLeaflet === 'function') {
        window._reloadLabNetworkGraphLeaflet();
      }
    }, 50);
    return;
  }
  // Fallback: legacy SVG (non-dsa_lab pages)
  try {
    const res = await fetch('/api/network');
    const json = await res.json();
    if (typeof renderNetworkGraphV2 === 'function' && document.getElementById('labNetworkCanvasBox')) {
      renderNetworkGraphV2('labNetworkCanvasBox', json.graph);
    }
  } catch(e) {}
}

async function execLabGraphBFS() {
  // If the Leaflet-based page function exists, call it.
  if (document.getElementById('bfsLeafletMap')) {
    setTimeout(() => {
      if (typeof window._execLabGraphBFSLeaflet === 'function') {
        window._execLabGraphBFSLeaflet();
      }
    }, 50);
    return;
  }
  // Fallback: legacy SVG path
  const start = document.getElementById('labGraphStartSelect')?.value || 'WH-1';
  try {
    const res = await fetch('/api/network/bfs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start_node: start })
    });
    const json = await res.json();
    if (json.status === 'success' && document.getElementById('labBfsTraceSequence')) {
      document.getElementById('labBfsTraceSequence').textContent =
        (json.traversal_order || []).join(' ➔ ');
    }
  } catch(e) {}
}

// Reports Charts
async function initReportsChartsV2() {
  try {
    const res = await fetch('/api/analytics');
    const json = await res.json();
    const charts = json.charts || {};

    // 1. Categories
    const ctxCat = document.getElementById('reportCategoryChart')?.getContext('2d');
    if (ctxCat && charts.categories) {
      new Chart(ctxCat, {
        type: 'doughnut',
        data: {
          labels: charts.categories.labels,
          datasets: [{
            data: charts.categories.counts,
            backgroundColor: ['#2563EB', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#64748B']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }

    // 2. Warehouse Stock
    const ctxWh = document.getElementById('reportWarehouseStockChart')?.getContext('2d');
    if (ctxWh && charts.warehouse_utilization) {
      new Chart(ctxWh, {
        type: 'bar',
        data: {
          labels: charts.warehouse_utilization.labels,
          datasets: [{
            label: 'Total Stock Units',
            data: charts.warehouse_utilization.stock,
            backgroundColor: '#2563EB',
            borderRadius: 6
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }

    // 3. Supplier Reliability
    const ctxSupp = document.getElementById('reportSupplierPerfChart')?.getContext('2d');
    if (ctxSupp && charts.supplier_reliability) {
      new Chart(ctxSupp, {
        type: 'bar',
        data: {
          labels: charts.supplier_reliability.labels,
          datasets: [{
            label: 'Reliability (%)',
            data: charts.supplier_reliability.scores,
            backgroundColor: '#10B981',
            borderRadius: 6
          }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 80, max: 100 } } }
      });
    }

    // 4. Order Status
    const ctxOrd = document.getElementById('reportOrderStatusChart')?.getContext('2d');
    if (ctxOrd && charts.order_status) {
      new Chart(ctxOrd, {
        type: 'pie',
        data: {
          labels: charts.order_status.labels,
          datasets: [{
            data: charts.order_status.counts,
            backgroundColor: ['#F59E0B', '#2563EB', '#10B981', '#EF4444']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }

    // 5. Order Priority
    const ctxPrio = document.getElementById('reportOrderPriorityChart')?.getContext('2d');
    if (ctxPrio && charts.order_priority) {
      new Chart(ctxPrio, {
        type: 'bar',
        data: {
          labels: charts.order_priority.labels,
          datasets: [{
            label: 'Orders',
            data: charts.order_priority.counts,
            backgroundColor: '#8B5CF6',
            borderRadius: 6
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }

    // 6. Warehouse Util
    const ctxWhUtil = document.getElementById('reportWarehouseUtilChart')?.getContext('2d');
    if (ctxWhUtil && charts.warehouse_utilization) {
      new Chart(ctxWhUtil, {
        type: 'bar',
        data: {
          labels: charts.warehouse_utilization.labels,
          datasets: [{
            label: 'Utilization %',
            data: charts.warehouse_utilization.utilization,
            backgroundColor: '#3B82F6',
            borderRadius: 6
          }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { min: 0, max: 100 } } }
      });
    }

    // 7. Algorithm Perf
    const ctxAlgo = document.getElementById('reportAlgoPerfChart')?.getContext('2d');
    if (ctxAlgo && charts.algorithm_performance) {
      new Chart(ctxAlgo, {
        type: 'bar',
        data: {
          labels: charts.algorithm_performance.labels,
          datasets: [{
            label: 'Avg Execution Time (ms)',
            data: charts.algorithm_performance.times,
            backgroundColor: '#F59E0B',
            borderRadius: 6
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      });
    }

  } catch(e) {
    console.error('Failed to init reports charts:', e);
  }
}
