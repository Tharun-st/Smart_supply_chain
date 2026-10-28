/**
 * Intelligent Supply Chain Management System
 * 21-Step Automated Academic Demonstration Controller
 */

let demoRunning = false;

function openDemoModal() {
  const modal = document.getElementById('demoModalOverlay');
  if (modal) {
    modal.classList.add('active');
    modal.style.display = 'flex';
  }
}

function closeDemoModal() {
  const modal = document.getElementById('demoModalOverlay');
  if (modal) {
    modal.classList.remove('active');
    modal.style.display = 'none';
  }
}

async function triggerFullDemo() {
  if (demoRunning) return;

  const startBtn = document.getElementById('startDemoBtn');
  const progressFill = document.getElementById('demoProgressFill');
  const stepIndicator = document.getElementById('demoStepIndicator');
  const percentIndicator = document.getElementById('demoPercentIndicator');
  const logContainer = document.getElementById('demoLogContainer');

  if (!logContainer) return;

  demoRunning = true;
  startBtn.disabled = true;
  startBtn.innerHTML = '<span>⏳</span> Executing Python DSA...';

  // Reset UI
  logContainer.innerHTML = '';
  progressFill.style.width = '0%';
  stepIndicator.textContent = 'Initializing Step 1...';
  percentIndicator.textContent = '0%';

  try {
    // Call the Python Flask backend endpoint
    const response = await fetch('/api/demo/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    const result = await response.json();

    if (result.status !== 'success') {
      throw new Error(result.message || 'Demo run failed');
    }

    const steps = result.steps;
    const totalSteps = steps.length;

    // Iterate through steps with smooth animated playback
    for (let i = 0; i < totalSteps; i++) {
      const step = steps[i];
      const pct = Math.round(((i + 1) / totalSteps) * 100);

      progressFill.style.width = `${pct}%`;
      stepIndicator.textContent = `Step ${step.step} / ${totalSteps}: ${step.title}`;
      percentIndicator.textContent = `${pct}%`;

      // Create step log card
      const card = document.createElement('div');
      card.className = 'demo-step-card animate-fade-in';
      card.style.cssText = `
        background: var(--bg-card, #ffffff);
        border: 1px solid var(--border-color, #e2e8f0);
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      `;

      let extraContent = '';
      if (step.chain_preview) {
        extraContent = `<div style="font-family: monospace; font-size: 0.8rem; background: rgba(37,99,235,0.06); padding: 4px 8px; border-radius: 4px; margin-top: 6px; color: #2563eb; word-break: break-all;">${step.chain_preview}</div>`;
      } else if (step.queue_preview) {
        extraContent = `<div style="font-family: monospace; font-size: 0.8rem; background: rgba(16,185,129,0.08); padding: 4px 8px; border-radius: 4px; margin-top: 6px; color: #059669;">${step.queue_preview}</div>`;
      } else if (step.traversal_result) {
        extraContent = `<div style="font-family: monospace; font-size: 0.8rem; background: rgba(139,92,246,0.08); padding: 4px 8px; border-radius: 4px; margin-top: 6px; color: #7c3aed;">In-Order: ${step.traversal_result}</div>`;
      } else if (step.traversal_preview) {
        extraContent = `<div style="font-family: monospace; font-size: 0.8rem; background: rgba(245,158,11,0.08); padding: 4px 8px; border-radius: 4px; margin-top: 6px; color: #d97706;">Order: ${step.traversal_preview}</div>`;
      } else if (step.selected_route) {
        extraContent = `<div style="font-family: monospace; font-size: 0.8rem; background: rgba(16,185,129,0.08); padding: 4px 8px; border-radius: 4px; margin-top: 6px; color: #059669;">Best Path: ${step.selected_route}</div>`;
      } else if (step.summary) {
        extraContent = `<div style="font-size: 0.8rem; margin-top: 6px; color: #64748b;">` +
          Object.entries(step.summary).map(([k, v]) => `<div>• <strong>${k}</strong>: ${v}</div>`).join('') +
          `</div>`;
      }

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; background: #2563eb; color: #ffffff; font-size: 0.72rem; font-weight: 700;">${step.step}</span>
            <strong style="font-size: 0.9rem; color: var(--text-primary, #0f172a);">${step.title}</strong>
          </div>
          <div style="display: flex; align-items: center; gap: 6px;">
            <span class="dsa-badge ${step.algorithm ? 'sort' : 'linked-list'}" style="font-size: 0.7rem; padding: 2px 6px;">${step.algorithm || step.data_structure || 'DSA'}</span>
            <span style="font-size: 0.72rem; color: #64748b; font-family: monospace;">${step.elapsed_ms} ms</span>
          </div>
        </div>
        <p style="margin: 6px 0 0 30px; font-size: 0.83rem; color: var(--text-secondary, #475569); line-height: 1.4;">
          ${step.detail}
        </p>
        <div style="margin-left: 30px;">${extraContent}</div>
      `;

      logContainer.appendChild(card);
      logContainer.scrollTop = logContainer.scrollHeight;

      // Small delay between steps to allow visual observation of progress
      await new Promise(r => setTimeout(r, 220));
    }

    // Success notification
    if (typeof showToast === 'function') {
      showToast(`21-Step Academic DSA Demo Completed in ${result.total_elapsed_ms} ms!`, 'success');
    }

    // Summary banner at the end of log
    const summaryCard = document.createElement('div');
    summaryCard.style.cssText = `
      background: #ecfdf5;
      border: 1px solid #10b981;
      border-radius: 8px;
      padding: 14px 18px;
      margin-top: 14px;
      color: #065f46;
      display: flex;
      justify-content: space-between;
      align-items: center;
    `;
    summaryCard.innerHTML = `
      <div>
        <strong style="font-size: 0.95rem;">🎉 Demonstration Complete!</strong>
        <p style="font-size: 0.82rem; margin: 4px 0 0 0;">All 16+ core Data Structures and Algorithmic paradigms successfully evaluated on Python Flask runtime.</p>
      </div>
      <div style="text-align: right;">
        <span style="font-size: 1.2rem; font-weight: 800; font-family: monospace;">${result.total_elapsed_ms} ms</span>
        <div style="font-size: 0.7rem; color: #047857;">Total Python Execution Time</div>
      </div>
    `;
    logContainer.appendChild(summaryCard);
    logContainer.scrollTop = logContainer.scrollHeight;

  } catch (err) {
    console.error('Demo execution error:', err);
    if (typeof showToast === 'function') {
      showToast(`Demo Error: ${err.message}`, 'error');
    }
    const errDiv = document.createElement('div');
    errDiv.style.cssText = 'background: #fef2f2; color: #991b1b; padding: 12px; border-radius: 6px; margin-top: 10px; font-size: 0.85rem;';
    errDiv.textContent = `Demo execution error: ${err.message}`;
    logContainer.appendChild(errDiv);
  } finally {
    demoRunning = false;
    startBtn.disabled = false;
    startBtn.innerHTML = '<span>🔄</span> Re-run Full Demo';
  }
}

// Global modal overlay click close
document.addEventListener('click', (e) => {
  const overlay = document.getElementById('demoModalOverlay');
  if (overlay && e.target === overlay) {
    closeDemoModal();
  }
});
