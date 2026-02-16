import { Drawer, Spin, Tag } from "antd";
import { useEffect, useState } from "react";

const GraphVisualization = () => {
  const [hoveredNode, setHoveredNode] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [tick, setTick] = useState(0);
  const [explainNode, setExplainNode] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [loadingExplain, setLoadingExplain] = useState(false);
  const [animating, setAnimating] = useState(false);
  const [targetNodes, setTargetNodes] = useState([]);
  const [simulate, setSimulate] = useState(true);

  useEffect(() => {
    let active = true;
    const fetchGraph = async () => {
      try {
        const base =
          import.meta.env.VITE_GATEWAY_URL || "http://localhost:5000";
        const resp = await fetch(`${base}/graph/network`);
        const data = await resp.json();
        if (!active) return;
        // Clustered radial layout by category with slight jitter to avoid static circle
        const width = 300;
        const height = 300;
        const cx = width / 2;
        const cy = height / 2;
        const baseRadius = 110;
        const categories = Array.from(
          new Set(data.nodes.map((n) => n.category || "unknown"))
        );
        // Pre-compute index within each category to avoid overlapping points
        const catCounts = {};
        const laidOut = data.nodes.map((n) => {
          const cat = n.category || "unknown";
          const catIndex = categories.indexOf(cat);
          const idxInCat = catCounts[cat] || 0;
          catCounts[cat] = idxInCat + 1;
          const catAngle =
            (2 * Math.PI * (catIndex + 0.5)) / Math.max(categories.length, 1);
          const spread = Math.max(1, catCounts[cat]);
          const angleOffset =
            ((idxInCat - (spread - 1) / 2) * Math.PI) / (8 + spread); // distribute within wedge
          const riskRadius = baseRadius - (n.risk || 0) * 40; // higher risk closer to center
          const x = cx + riskRadius * Math.cos(catAngle + angleOffset);
          const y = cy + riskRadius * Math.sin(catAngle + angleOffset);
          // dynamic jitter per node id to avoid tight stacking
          const idHash =
            (String(n.tx_id || n.id)
              .split("")
              .reduce((a, c) => a + c.charCodeAt(0), 0) %
              5) -
            2;
          const dynJitter = ((tick % 7) - 3) * 0.4 + idHash * 0.6;
          return { ...n, x: x + dynJitter, y: y - dynJitter };
        });
        let normalized = laidOut.map((n) => ({
          ...n,
          risk: n.risk > 1 ? Math.min(n.risk / 100, 1) : n.risk,
        }));
        // Lightweight force simulation for separation
        if (simulate && normalized.length) {
          const maxIter = 20; // small number to keep perf in check
          const w = 300,
            h = 300;
          for (let iter = 0; iter < maxIter; iter++) {
            // Repulsion
            for (let i = 0; i < normalized.length; i++) {
              for (let j = i + 1; j < normalized.length; j++) {
                const a = normalized[i];
                const b = normalized[j];
                let dx = a.x - b.x;
                let dy = a.y - b.y;
                let dist2 = dx * dx + dy * dy + 0.001;
                const minDist = 14; // target separation
                if (dist2 < minDist * minDist) {
                  const force = 0.4 / Math.sqrt(dist2);
                  dx *= force;
                  dy *= force;
                  a.x += dx;
                  a.y += dy;
                  b.x -= dx;
                  b.y -= dy;
                }
              }
            }
            // Link springs
            (data.links || []).forEach((lk) => {
              const a = normalized[lk.source];
              const b = normalized[lk.target];
              if (!a || !b) return;
              let dx = b.x - a.x;
              let dy = b.y - a.y;
              const target = 40; // desired link length
              const dist = Math.sqrt(dx * dx + dy * dy) + 0.001;
              const k = 0.05; // spring constant
              const delta = (dist - target) * k;
              dx = (dx / dist) * delta;
              dy = (dy / dist) * delta;
              a.x += dx;
              a.y += dy;
              b.x -= dx;
              b.y -= dy;
            });
            // Bounds
            for (let i = 0; i < normalized.length; i++) {
              normalized[i].x = Math.max(15, Math.min(w - 15, normalized[i].x));
              normalized[i].y = Math.max(15, Math.min(h - 15, normalized[i].y));
            }
          }
        }
        // Animate from previous positions to new positions over ~600ms
        if (nodes.length && normalized.length && !animating) {
          const start = performance.now();
          const duration = 600;
          const startNodes = nodes;
          // Map by id for interpolation
          const startById = Object.fromEntries(
            startNodes.map((n) => [n.id, n])
          );
          setTargetNodes(normalized);
          setAnimating(true);
          const step = (now) => {
            const t = Math.min(1, (now - start) / duration);
            const interp = normalized.map((n) => {
              const s = startById[n.id] || n;
              return {
                ...n,
                x: s.x + (n.x - s.x) * t,
                y: s.y + (n.y - s.y) * t,
              };
            });
            setNodes(interp);
            if (t < 1) {
              requestAnimationFrame(step);
            } else {
              setAnimating(false);
            }
          };
          requestAnimationFrame(step);
        } else {
          setNodes(normalized);
        }
        setLinks(data.links || []);
      } catch (e) {
        // Fallback random small graph on error
        const fallbackNodes = Array.from({ length: 10 }, (_, i) => ({
          id: i,
          risk: Math.random(),
          connections: 0,
          x: 40 + (i % 5) * 45,
          y: 60 + Math.floor(i / 5) * 80,
        }));
        setNodes(fallbackNodes);
        setLinks([]);
      }
    };
    fetchGraph();
    const interval = setInterval(() => {
      setTick((t) => t + 1);
      fetchGraph();
    }, 5000); // refresh every 5s
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const handleExplain = async (node) => {
    setExplainNode(node);
    setLoadingExplain(true);
    setExplanation(null);
    const txId = node.tx_id || node.id;
    try {
      const resp = await fetch(`http://localhost:5000/events/explain/${txId}`);
      const data = await resp.json();
      setExplanation(data);
    } catch (e) {
      setExplanation({ error: "Failed to fetch explanation" });
    } finally {
      setLoadingExplain(false);
    }
  };

  return (
    <div
      style={{
        height: 300,
        position: "relative",
        overflow: "hidden",
        background: "#fafafa",
        borderRadius: 8,
      }}
    >
      <svg width="100%" height="100%" viewBox="0 0 300 300">
        {/* Links */}
        {links.map((link, i) => {
          const source = nodes[link.source];
          const target = nodes[link.target];
          if (!source || !target) return null;
          return (
            <line
              key={i}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="#ddd"
              strokeWidth="1"
            />
          );
        })}

        {/* Nodes */}
        {nodes.map((node) => (
          <g
            key={node.id}
            onMouseEnter={() => setHoveredNode(node)}
            onMouseLeave={() => setHoveredNode(null)}
            onClick={() => handleExplain(node)}
            style={{ cursor: "pointer" }}
          >
            <circle
              cx={node.x}
              cy={node.y}
              r={node.risk > 0.8 ? 9 : node.risk > 0.5 ? 7 : 5}
              fill={
                node.risk > 0.8
                  ? "#ff4d4f"
                  : node.risk > 0.5
                  ? "#faad14"
                  : "#52c41a"
              }
              stroke="#fff"
              strokeWidth="2"
              style={{
                transition: "all 0.3s",
                filter:
                  hoveredNode?.id === node.id
                    ? "drop-shadow(0 0 4px rgba(0,0,0,0.3))"
                    : "none",
                transformOrigin: `${node.x}px ${node.y}px`,
                transform:
                  hoveredNode?.id === node.id ? "scale(1.5)" : "scale(1)",
              }}
            />
          </g>
        ))}
      </svg>

      {/* Tooltip Overlay */}
      {hoveredNode && (
        <div
          style={{
            position: "absolute",
            top: hoveredNode.y - 40,
            left: hoveredNode.x,
            transform: "translateX(-50%)",
            background: "rgba(0,0,0,0.8)",
            color: "#fff",
            padding: "4px 8px",
            borderRadius: 4,
            fontSize: 12,
            pointerEvents: "none",
            zIndex: 10,
            whiteSpace: "nowrap",
          }}
        >
          ID: {hoveredNode.id} | Risk: {(hoveredNode.risk * 100).toFixed(0)}%{" "}
          {hoveredNode.amount ? `| Amt: $${hoveredNode.amount}` : ""}
        </div>
      )}

      <div
        style={{
          position: "absolute",
          bottom: 10,
          right: 10,
          fontSize: 10,
          color: "#999",
          display: "flex",
          gap: 8,
        }}
      >
        <span style={{ color: "#ff4d4f" }}>● High</span>
        <span style={{ color: "#faad14" }}>● Medium</span>
        <span style={{ color: "#52c41a" }}>● Low</span>
        <span style={{ marginLeft: 8 }}>
          <label style={{ cursor: "pointer" }}>
            <input
              type="checkbox"
              checked={simulate}
              onChange={(e) => setSimulate(e.target.checked)}
              style={{ marginRight: 4 }}
            />
            Force
          </label>
        </span>
      </div>

      <Drawer
        title={
          explainNode
            ? `Explanation: ${explainNode.tx_id || explainNode.id}`
            : "Explanation"
        }
        placement="right"
        open={!!explainNode}
        onClose={() => {
          setExplainNode(null);
          setExplanation(null);
        }}
        width={360}
      >
        {loadingExplain && <Spin size="small" />}
        {!loadingExplain && explanation && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div>
              <Tag
                color={
                  explainNode.risk > 0.8
                    ? "red"
                    : explainNode.risk > 0.5
                    ? "orange"
                    : "green"
                }
              >
                Risk {(explainNode.risk * 100).toFixed(1)}%
              </Tag>
            </div>
            <div>
              <strong>Score:</strong>{" "}
              {explanation?.explanation?.score?.toFixed?.(4) ||
                explanation?.score}
            </div>
            <div>
              <strong>Feature Attributions:</strong>
              <ul style={{ paddingLeft: 16 }}>
                {Object.entries(
                  explanation?.explanation?.feature_attributions || {}
                ).map(([k, v]) => (
                  <li key={k} style={{ fontSize: 12 }}>
                    {k}: {Number(v).toFixed(4)}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <strong>Meta:</strong>
              <pre style={{ fontSize: 11 }}>
                {JSON.stringify(explanation?.explanation?.meta || {}, null, 2)}
              </pre>
            </div>
          </div>
        )}
        {!loadingExplain && !explanation && (
          <div style={{ fontSize: 12, color: "#999" }}>
            Click a node to load an explanation.
          </div>
        )}
      </Drawer>
    </div>
  );
};

// (Removed external placeholder; handler defined inside component)

export default GraphVisualization;
