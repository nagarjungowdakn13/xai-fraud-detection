import { Spin, Tooltip } from "antd";
import { useEffect, useState } from "react";

const FraudHeatmap = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const fetchHeatmap = () => {
      const base = import.meta.env.VITE_GATEWAY_URL || "http://localhost:5000";
      fetch(`${base}/analytics/heatmap`, { cache: "no-store" })
        .then((r) => r.json())
        .then((d) => {
          if (active) {
            setData(d);
            setLoading(false);
          }
        })
        .catch(() => setLoading(false));
    };
    fetchHeatmap();
    const interval = setInterval(fetchHeatmap, 10000); // refresh every 10s
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const getColor = (avgRisk, count) => {
    // Blend risk and count: normalize count impact (cap at 25)
    const normCount = Math.min(count, 25) / 25; // 0..1
    const composite = avgRisk * 0.7 + normCount * 0.3;
    const intensity = Math.floor(composite * 255);
    return `rgba(255, ${255 - intensity}, 0, ${0.35 + composite * 0.55})`;
  };

  return (
    <div
      style={{
        height: 300,
        display: "flex",
        flexDirection: "column",
        padding: 10,
      }}
    >
      <div style={{ display: "flex", flex: 1 }}>
        {/* Y-Axis Labels (Days) */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-around",
            paddingRight: 10,
          }}
        >
          {data &&
            data.map((d) => (
              <span key={d.day} style={{ fontSize: 12, color: "#666" }}>
                {d.day}
              </span>
            ))}
        </div>

        {/* Grid */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            flex: 1,
            justifyContent: "space-between",
          }}
        >
          {loading && (
            <div
              style={{
                display: "flex",
                flex: 1,
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Spin size="small" />
            </div>
          )}
          {!loading &&
            data &&
            data.map((row, i) => (
              <div
                key={i}
                style={{ display: "flex", flex: 1, marginBottom: 2 }}
              >
                {row.slots.map((slot, j) => (
                  <Tooltip
                    key={j}
                    title={`${row.day} ${slot.start}: ${
                      slot.count
                    } Events (Avg Risk: ${(slot.avg_risk * 100).toFixed(0)}%)`}
                  >
                    <div
                      style={{
                        flex: 1,
                        marginRight: 2,
                        backgroundColor: getColor(slot.avg_risk, slot.count),
                        borderRadius: 2,
                        cursor: "pointer",
                        transition: "all 0.2s",
                      }}
                      onMouseEnter={(e) => (e.target.style.opacity = 0.7)}
                      onMouseLeave={(e) => (e.target.style.opacity = 1)}
                    />
                  </Tooltip>
                ))}
              </div>
            ))}
        </div>
      </div>

      {/* X-Axis Labels (Hours) */}
      <div
        style={{
          display: "flex",
          marginLeft: 30,
          justifyContent: "space-between",
          marginTop: 5,
        }}
      >
        {data &&
          data[0].slots
            .filter((_, i) => i % 2 === 0)
            .map((slot, i) => (
              <span key={i} style={{ fontSize: 10, color: "#999" }}>
                {slot.start}
              </span>
            ))}
      </div>
    </div>
  );
};

export default FraudHeatmap;
