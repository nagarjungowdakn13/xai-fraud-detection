import {
  Card,
  Col,
  Descriptions,
  Modal,
  Row,
  Space,
  Statistic,
  Table,
  Tag,
  Typography,
} from "antd";
import {
  Activity,
  AlertOctagon,
  ShieldCheck,
  TrendingUp,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { FraudHeatmap, GraphVisualization, RealTimeChart } from "../components";

const { Title, Text } = Typography;

const Dashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [realtimeData, setRealtimeData] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    highRisk: 0,
    avgScore: 0,
  });

  const [selectedTx, setSelectedTx] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [explLoading, setExplLoading] = useState(false);
  const [explVisible, setExplVisible] = useState(false);

  useEffect(() => {
    // Fetch real-time data from gateway (avoid dev server origin)
    const GATEWAY = import.meta.env.VITE_GATEWAY_URL || "http://localhost:5000";

    let cancelled = false;

    // Seed the dashboard with recent events so history is preserved
    // when navigating between pages in the UI.
    fetch(`${GATEWAY}/events/recent`)
      .then((r) => r.json())
      .then((events) => {
        if (cancelled || !Array.isArray(events)) return;

        const sorted = [...events].sort(
          (a, b) => (a.time || 0) - (b.time || 0),
        );

        const withDisplayTime = sorted.map((e) => ({
          ...e,
          time: e.time
            ? new Date(e.time * 1000).toLocaleTimeString()
            : new Date().toLocaleTimeString(),
        }));

        // Use last 20 points for chart
        setRealtimeData(withDisplayTime.slice(-20));
        // Most recent first for alerts table
        const reversed = [...withDisplayTime].reverse();
        setAlerts(reversed.slice(0, 10));

        // Initialise stats from this history so counts don't reset
        if (withDisplayTime.length) {
          const total = withDisplayTime.length;
          const highRisk = withDisplayTime.filter(
            (e) => e.risk_score > 0.8,
          ).length;
          const avgScore =
            withDisplayTime.reduce((acc, e) => acc + (e.risk_score || 0), 0) /
            total;
          setStats({ total, highRisk, avgScore });
        }
      })
      .catch(() => {});

    const eventSource = new EventSource(`${GATEWAY}/fraud/stream`);
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Add timestamp for chart
      const dataWithTime = { ...data, time: new Date().toLocaleTimeString() };

      setRealtimeData((prev) => {
        const newData = [...prev, dataWithTime];
        return newData.slice(-20); // Keep last 20 points for chart
      });

      setAlerts((prev) => {
        const newAlerts = [dataWithTime, ...prev];
        return newAlerts.slice(0, 10); // Keep last 10 alerts in table
      });

      // Update stats
      setStats((prev) => ({
        total: prev.total + 1,
        highRisk: data.risk_score > 0.8 ? prev.highRisk + 1 : prev.highRisk,
        avgScore:
          (prev.avgScore * prev.total + data.risk_score) / (prev.total + 1),
      }));
    };

    return () => {
      cancelled = true;
      eventSource.close();
    };
  }, []);

  const columns = [
    {
      title: "Time",
      dataIndex: "time",
      key: "time",
      width: 100,
      render: (text) => <Text type="secondary">{text}</Text>,
    },
    {
      title: "Transaction ID",
      dataIndex: "id",
      key: "id",
      render: (text) => (
        <Text strong copyable>
          {text}
        </Text>
      ),
    },
    {
      title: "Amount",
      dataIndex: "amount",
      key: "amount",
      render: (val) => `₹${val}`,
    },
    {
      title: "Risk Score",
      dataIndex: "risk_score",
      key: "risk_score",
      render: (score) => (
        <Tag color={score > 0.8 ? "red" : score > 0.6 ? "orange" : "green"}>
          {score.toFixed(2)}
        </Tag>
      ),
    },
    {
      title: "Action",
      dataIndex: "recommendation",
      key: "recommendation",
      render: (text) => {
        let color = "default";
        if (text === "Reject") color = "error";
        if (text === "Approve") color = "success";
        if (text === "Review") color = "warning";
        return <Tag color={color}>{text.toUpperCase()}</Tag>;
      },
    },
  ];

  const handleRowClick = (record) => {
    setSelectedTx(record);
    setExplVisible(true);
    setExplLoading(true);
    fetch(`/events/explain/${record.id}`)
      .then((r) => r.json())
      .then((data) => {
        setExplanation(data);
        setExplLoading(false);
      })
      .catch(() => {
        setExplanation({ error: "Failed to load explanation" });
        setExplLoading(false);
      });
  };

  return (
    <div style={{ padding: "24px" }}>
      <div
        style={{
          marginBottom: 24,
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <Zap size={28} color="#1677ff" />
        <Title level={2} style={{ margin: 0 }}>
          Live Fraud Monitoring
        </Title>
      </div>

      {/* Top Stats Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} hoverable>
            <Statistic
              title="Total Processed"
              value={stats.total}
              prefix={<Activity size={20} />}
              valueStyle={{ color: "#1677ff" }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} hoverable>
            <Statistic
              title="High Risk Detected"
              value={stats.highRisk}
              valueStyle={{ color: "#cf1322" }}
              prefix={<AlertOctagon size={20} />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} hoverable>
            <Statistic
              title="Avg Risk Score"
              value={stats.avgScore}
              precision={2}
              prefix={<TrendingUp size={20} />}
              suffix="/ 1.0"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} hoverable>
            <Statistic
              title="System Status"
              value="Active"
              valueStyle={{ color: "#3f8600" }}
              prefix={<ShieldCheck size={20} />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Left Column: Charts */}
        <Col xs={24} lg={16}>
          <Space direction="vertical" size="large" style={{ width: "100%" }}>
            <Card title="Real-time Risk Trend" bordered={false} hoverable>
              <RealTimeChart data={realtimeData} />
            </Card>

            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Card
                  title="Geographic Heatmap"
                  bordered={false}
                  hoverable
                  bodyStyle={{ padding: 0, height: 300 }}
                >
                  <FraudHeatmap />
                </Card>
              </Col>
              <Col span={12}>
                <Card
                  title="Network Analysis"
                  bordered={false}
                  hoverable
                  bodyStyle={{ padding: 0, height: 300 }}
                >
                  <GraphVisualization />
                </Card>
              </Col>
            </Row>
          </Space>
        </Col>

        {/* Right Column: Live Feed */}
        <Col xs={24} lg={8}>
          <Card
            title="Live Transaction Feed"
            bordered={false}
            hoverable
            extra={<Tag color="processing">Live</Tag>}
            bodyStyle={{ padding: 0 }}
          >
            <Table
              dataSource={alerts}
              columns={columns}
              rowKey="id"
              onRow={(record) => ({
                onClick: () => handleRowClick(record),
                style: { cursor: "pointer" },
              })}
              pagination={false}
              size="small"
              scroll={{ y: 600 }}
            />
          </Card>
        </Col>
      </Row>

      <Modal
        title="Transaction Explanation"
        open={explVisible}
        onCancel={() => setExplVisible(false)}
        footer={null}
        width={720}
      >
        {explLoading && <p>Loading explanation...</p>}
        {!explLoading && selectedTx && (
          <Space direction="vertical" style={{ width: "100%" }} size="large">
            <Descriptions bordered column={2} size="small">
              <Descriptions.Item label="Transaction ID">
                {selectedTx.id}
              </Descriptions.Item>
              <Descriptions.Item label="Amount">
                ₹{selectedTx.amount}
              </Descriptions.Item>
              <Descriptions.Item label="Risk Score">
                {selectedTx.risk_score?.toFixed(4)}
              </Descriptions.Item>
              <Descriptions.Item label="Recommendation">
                {selectedTx.recommendation}
              </Descriptions.Item>
            </Descriptions>

            {Array.isArray(selectedTx.rules) && selectedTx.rules.length > 0 && (
              <div>
                <Title level={5} style={{ marginTop: 16 }}>
                  Decision Reasons
                </Title>
                {selectedTx.rules.map((r, idx) => (
                  <div key={idx} style={{ fontSize: 13 }}>
                    • {r}
                  </div>
                ))}
              </div>
            )}

            {explanation &&
              explanation.explanation &&
              explanation.explanation.summary &&
              explanation.explanation.summary.human_readable && (
                <div>
                  <Title level={5} style={{ marginTop: 16 }}>
                    Plain-language explanation
                  </Title>
                  <div style={{ fontSize: 13 }}>
                    {explanation.explanation.summary.human_readable}
                  </div>
                </div>
              )}

            {explanation &&
              explanation.explanation &&
              explanation.explanation.feature_attributions && (
                <div>
                  <Title level={5} style={{ marginTop: 16 }}>
                    Feature contributions (technical view)
                  </Title>
                  {Object.entries(explanation.explanation.feature_attributions)
                    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
                    .slice(0, 5)
                    .map(([name, value]) => {
                      const info =
                        explanation.explanation.feature_info &&
                        explanation.explanation.feature_info[name];
                      const label = info?.name || name;
                      const direction =
                        value > 0 ? "↑ increases risk" : "↓ reduces risk";
                      return (
                        <div
                          key={name}
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            fontSize: 13,
                            gap: 8,
                          }}
                        >
                          <span>
                            <strong>{label}</strong>
                            {info?.description && (
                              <span style={{ marginLeft: 4, opacity: 0.8 }}>
                                – {info.description}
                              </span>
                            )}
                          </span>
                          <span>
                            {Number(value).toFixed(4)} ({direction})
                          </span>
                        </div>
                      );
                    })}
                </div>
              )}

            {explanation && explanation.error && (
              <Tag color="red">{explanation.error}</Tag>
            )}
          </Space>
        )}
      </Modal>
    </div>
  );
};

export default Dashboard;
