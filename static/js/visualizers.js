/**
 * Intelligent Supply Chain Optimization System (ISCS)
 * Dynamic DSA Visualizers & Canvas Rendering Engines
 */

// ==================== 1. LINKED LIST VISUALIZER ====================
function renderLinkedListV2(containerId, visualNodes, highlightKey = null) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '';

  if (!visualNodes || visualNodes.length === 0) {
    container.innerHTML = `
      <div class="ll-head-tag">HEAD</div>
      <div class="ll-arrow">➔</div>
      <div class="ll-null-tag">NULL</div>
      <span style="color:var(--color-text-muted); margin-left:12px; font-style:italic; font-size:0.8rem;">
        Linked List is empty (HEAD ➔ NULL)
      </span>
    `;
    return;
  }

  // HEAD tag
  const headEl = document.createElement('div');
  headEl.className = 'll-head-tag';
  headEl.textContent = 'HEAD';
  container.appendChild(headEl);

  const headArrow = document.createElement('div');
  headArrow.className = 'll-arrow';
  headArrow.textContent = '➔';
  container.appendChild(headArrow);

  visualNodes.forEach((node, idx) => {
    const isHighlight = highlightKey !== null && (String(node.node_id).toLowerCase() === String(highlightKey).toLowerCase() || String(node.label).toLowerCase().includes(String(highlightKey).toLowerCase()));

    const nodeEl = document.createElement('div');
    nodeEl.className = `ll-node-box ${isHighlight ? 'highlight' : ''}`;
    nodeEl.id = `ll-node-${idx}`;

    nodeEl.innerHTML = `
      <div class="ll-node-data">
        <span class="ll-node-key">#${node.node_id || idx}</span>
        <span class="ll-node-val" title="${node.label}">${node.label || 'Node'}</span>
      </div>
      <div class="ll-node-ptr">
        <span>next •</span>
      </div>
    `;
    container.appendChild(nodeEl);

    // Arrow to next or NULL
    const arrow = document.createElement('div');
    arrow.className = 'll-arrow';
    arrow.textContent = '➔';
    container.appendChild(arrow);
  });

  // NULL tag
  const nullEl = document.createElement('div');
  nullEl.className = 'll-null-tag';
  nullEl.textContent = 'NULL';
  container.appendChild(nullEl);
}

// ==================== 2. FIFO QUEUE VISUALIZER ====================
function renderQueueV2(containerId, queueNodes) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '';

  if (!queueNodes || queueNodes.length === 0) {
    container.innerHTML = `
      <div style="color:var(--color-text-muted); font-style:italic; padding:16px; font-size:0.85rem;">
        Queue is empty. Ready for incoming orders.
      </div>
    `;
    return;
  }

  queueNodes.forEach((node, idx) => {
    const isFront = idx === 0;
    const isRear = idx === queueNodes.length - 1;

    const cell = document.createElement('div');
    cell.className = `queue-cell-item ${isFront ? 'front' : ''} ${isRear ? 'rear' : ''}`;

    let label = node.label || node.data?.order_number || `#${node.id || idx + 1}`;
    let sub = node.data?.customer_name ? node.data.customer_name : `Pos ${idx + 1}`;

    cell.innerHTML = `
      ${isFront ? '<div style="font-size:0.65rem; font-weight:800; color:var(--color-success); margin-bottom:2px;">[FRONT]</div>' : ''}
      ${isRear && !isFront ? '<div style="font-size:0.65rem; font-weight:800; color:var(--color-primary-blue); margin-bottom:2px;">[REAR]</div>' : ''}
      <div style="font-weight:700; font-size:0.9rem; color:var(--color-text);">${label}</div>
      <div style="font-size:0.72rem; color:var(--color-text-muted); margin-top:2px;">${sub}</div>
    `;
    container.appendChild(cell);

    if (!isRear) {
      const arrow = document.createElement('div');
      arrow.style.cssText = 'color:var(--color-primary-blue); font-size:1.1rem; font-weight:bold;';
      arrow.textContent = '➔';
      container.appendChild(arrow);
    }
  });
}

// ==================== 3. BST TREE SVG VISUALIZER ====================
function renderBSTTreeV2(containerId, rootNode, highlightPath = []) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '';

  if (!rootNode) {
    container.innerHTML = '<div style="color:var(--color-text-muted); padding:30px; font-size:0.85rem;">BST is empty. Insert a key above.</div>';
    return;
  }

  const nodes = [];
  const lines = [];

  function layoutTree(node, x, y, offset, depth) {
    if (!node) return;
    nodes.push({ key: node.key, x, y, data: node.data });
    const nextY = y + 70;
    const nextOffset = Math.max(offset * 0.52, 35);

    if (node.left) {
      const leftX = x - offset;
      lines.push({ x1: x, y1: y, x2: leftX, y2: nextY });
      layoutTree(node.left, leftX, nextY, nextOffset, depth + 1);
    }
    if (node.right) {
      const rightX = x + offset;
      lines.push({ x1: x, y1: y, x2: rightX, y2: nextY });
      layoutTree(node.right, rightX, nextY, nextOffset, depth + 1);
    }
  }

  const rootX = 350;
  const rootY = 40;
  layoutTree(rootNode, rootX, rootY, 140, 0);

  let minX = rootX, maxX = rootX, maxY = rootY;
  nodes.forEach(n => {
    if (n.x < minX) minX = n.x;
    if (n.x > maxX) maxX = n.x;
    if (n.y > maxY) maxY = n.y;
  });

  const width = Math.max(maxX - minX + 100, 700);
  const height = Math.max(maxY + 60, 320);
  const shiftX = (width / 2) - rootX;

  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", height);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  // Lines
  lines.forEach(l => {
    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", l.x1 + shiftX);
    line.setAttribute("y1", l.y1);
    line.setAttribute("x2", l.x2 + shiftX);
    line.setAttribute("y2", l.y2);
    line.setAttribute("stroke", "#CBD5E1");
    line.setAttribute("stroke-width", "2");
    svg.appendChild(line);
  });

  // Nodes
  nodes.forEach(n => {
    const isHigh = highlightPath.includes(n.key);
    const g = document.createElementNS(svgNS, "g");

    const circle = document.createElementNS(svgNS, "circle");
    circle.setAttribute("cx", n.x + shiftX);
    circle.setAttribute("cy", n.y);
    circle.setAttribute("r", "20");
    circle.setAttribute("fill", isHigh ? "#2563EB" : "#FFFFFF");
    circle.setAttribute("stroke", isHigh ? "#1D4ED8" : "#2563EB");
    circle.setAttribute("stroke-width", isHigh ? "3" : "2");
    circle.style.cursor = "pointer";

    const text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", n.x + shiftX);
    text.setAttribute("y", n.y + 5);
    text.setAttribute("fill", isHigh ? "#FFFFFF" : "#0F172A");
    text.setAttribute("font-size", "12px");
    text.setAttribute("font-weight", "700");
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("font-family", "monospace");
    text.textContent = n.key;

    g.appendChild(circle);
    g.appendChild(text);
    svg.appendChild(g);
  });

  container.appendChild(svg);
}

// ==================== 4. NETWORK GRAPH SVG VISUALIZER ====================
function renderNetworkGraphV2(containerId, graphData, activeHighlightNodes = []) {
  const container = document.getElementById(containerId);
  if (!container || !graphData) return;

  const nodes = graphData.nodes || [];
  const links = graphData.links || [];
  const width = container.clientWidth || 800;
  const height = 400;

  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(centerX, centerY) - 70;

  const nodeMap = {};
  nodes.forEach((n, idx) => {
    const angle = (idx / nodes.length) * 2 * Math.PI;
    const r = n.type === 'warehouse' ? radius * 0.6 : radius;
    nodeMap[n.id] = {
      ...n,
      x: centerX + r * Math.cos(angle),
      y: centerY + r * Math.sin(angle)
    };
  });

  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("id", "networkGraphSvg");
  svg.setAttribute("width", "100%");
  svg.setAttribute("height", height);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  // Links
  links.forEach(l => {
    const src = nodeMap[l.source];
    const dst = nodeMap[l.target];
    if (src && dst) {
      const line = document.createElementNS(svgNS, "line");
      line.setAttribute("x1", src.x);
      line.setAttribute("y1", src.y);
      line.setAttribute("x2", dst.x);
      line.setAttribute("y2", dst.y);
      line.setAttribute("stroke", "rgba(255,255,255,0.18)");
      line.setAttribute("stroke-width", "1.5");
      svg.appendChild(line);

      const label = document.createElementNS(svgNS, "text");
      label.setAttribute("x", (src.x + dst.x) / 2);
      label.setAttribute("y", (src.y + dst.y) / 2 - 4);
      label.setAttribute("fill", "#64748B");
      label.setAttribute("font-size", "9px");
      label.setAttribute("font-family", "monospace");
      label.textContent = `${l.distance_km}km`;
      svg.appendChild(label);
    }
  });

  // Nodes
  Object.values(nodeMap).forEach(n => {
    const isVisited = activeHighlightNodes.includes(n.id);
    const g = document.createElementNS(svgNS, "g");
    g.setAttribute("id", `graph-node-${n.id}`);

    const circle = document.createElementNS(svgNS, "circle");
    circle.setAttribute("cx", n.x);
    circle.setAttribute("cy", n.y);
    circle.setAttribute("r", isVisited ? "19" : "15");
    circle.setAttribute("fill", isVisited ? "#F59E0B" : (n.type === 'warehouse' ? "#2563EB" : "#10B981"));
    circle.setAttribute("stroke", isVisited ? "#FFFFFF" : "rgba(255,255,255,0.3)");
    circle.setAttribute("stroke-width", isVisited ? "3" : "1.5");

    const text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", n.x);
    text.setAttribute("y", n.y + 24);
    text.setAttribute("fill", "#F8FAFC");
    text.setAttribute("font-size", "10px");
    text.setAttribute("font-weight", "600");
    text.setAttribute("text-anchor", "middle");
    text.textContent = n.name || n.id;

    g.appendChild(circle);
    g.appendChild(text);
    svg.appendChild(g);
  });

  container.innerHTML = '';
  container.appendChild(svg);
}
