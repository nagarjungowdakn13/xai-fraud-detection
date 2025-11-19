import { Card, Col, Row, Space, Statistic, Table, Tag, Typography } from "antd";
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

  useEffect(() => {
    // Fetch real-time data
    const eventSource = new EventSource("/fraud/stream");
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

    return () => eventSource.close();
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
              pagination={false}
              size="small"
              scroll={{ y: 600 }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
