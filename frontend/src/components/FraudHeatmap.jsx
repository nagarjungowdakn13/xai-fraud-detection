import { Tooltip } from "antd";
import { useMemo } from "react";

const FraudHeatmap = () => {
  // Generate mock data for a 7x12 grid (Days x 2-hour blocks)
  const data = useMemo(() => {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const hours = Array.from({ length: 12 }, (_, i) => `${i * 2}:00`);

    return days.map((day) => ({
      day,
      slots: hours.map((hour) => ({
        hour,
        value: Math.random(), // 0 to 1 intensity
        count: Math.floor(Math.random() * 50),
      })),
    }));
  }, []);

  const getColor = (value) => {
    // Heatmap color scale (Light Yellow to Deep Red)
    const intensity = Math.floor(value * 255);
    return `rgba(255, ${255 - intensity}, 0, ${0.3 + value * 0.7})`;
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
          {data.map((d) => (
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
          {data.map((row, i) => (
            <div key={i} style={{ display: "flex", flex: 1, marginBottom: 2 }}>
              {row.slots.map((slot, j) => (
                <Tooltip
                  key={j}
                  title={`${row.day} ${slot.hour}: ${
                    slot.count
                  } Alerts (Risk: ${(slot.value * 100).toFixed(0)}%)`}
                >
                  <div
                    style={{
                      flex: 1,
                      marginRight: 2,
                      backgroundColor: getColor(slot.value),
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
        {data[0].slots
          .filter((_, i) => i % 2 === 0)
          .map((slot, i) => (
            <span key={i} style={{ fontSize: 10, color: "#999" }}>
              {slot.hour}
            </span>
          ))}
      </div>
    </div>
  );
};

export default FraudHeatmap;
