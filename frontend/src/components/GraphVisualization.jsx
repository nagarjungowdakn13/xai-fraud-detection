import { useMemo, useState } from "react";

const GraphVisualization = () => {
  const [hoveredNode, setHoveredNode] = useState(null);

  // Generate random graph data
  const { nodes, links } = useMemo(() => {
    const nodeCount = 15;
    const nodes = Array.from({ length: nodeCount }, (_, i) => ({
      id: i,
      x: Math.random() * 280 + 10, // Random X (10-290)
      y: Math.random() * 280 + 10, // Random Y (10-290)
      risk: Math.random(),
      connections: 0,
    }));

    const links = [];
    nodes.forEach((node, i) => {
      // Connect to 1-3 random other nodes
      const numLinks = Math.floor(Math.random() * 3) + 1;
      for (let j = 0; j < numLinks; j++) {
        const targetId = Math.floor(Math.random() * nodeCount);
        if (targetId !== i) {
          links.push({ source: i, target: targetId });
          nodes[i].connections++;
          nodes[targetId].connections++;
        }
      }
    });

    return { nodes, links };
  }, []);

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
            style={{ cursor: "pointer" }}
          >
            <circle
              cx={node.x}
              cy={node.y}
              r={node.risk > 0.8 ? 8 : 5}
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
          ID: {hoveredNode.id} | Risk: {(hoveredNode.risk * 100).toFixed(0)}%
        </div>
      )}

      <div
        style={{
          position: "absolute",
          bottom: 10,
          right: 10,
          fontSize: 10,
          color: "#999",
        }}
      >
        <span style={{ color: "#ff4d4f" }}>●</span> High Risk
        <span style={{ color: "#52c41a", marginLeft: 8 }}>●</span> Low Risk
      </div>
    </div>
  );
};

export default GraphVisualization;
