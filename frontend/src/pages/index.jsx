import {
  Badge,
  Button,
  Card,
  Col,
  Descriptions,
  Modal,
  Progress,
  Row,
  Statistic,
  Table,
  Tag,
  Typography,
} from "antd";
import {
  Activity,
  AlertTriangle,
  CreditCard,
  RefreshCw,
  Search,
} from "lucide-react";
import { useEffect, useState } from "react";

const { Title } = Typography;

export default function Home() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTx, setSelectedTx] = useState(null);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [metrics, setMetrics] = useState(null);

  const fetchTransactions = () => {
    setLoading(true);
    fetch("/fraud/transactions", { cache: "no-store" })
      .then((response) => response.json())
      .then((data) => {
        setTransactions(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch transactions", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchTransactions();
    let active = true;
    const fetchMetrics = () => {
      fetch("/metrics", { cache: "no-store" })
        .then((r) => r.json())
        .then((m) => {
          if (active) setMetrics(m);
        })
        .catch(() => {});
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  // Subscribe to the same live stream as the dashboard so that
  // new transactions appear in the overview table in real time.
  useEffect(() => {
    const GATEWAY = import.meta.env.VITE_GATEWAY_URL || "http://localhost:5000";
    const eventSource = new EventSource(`${GATEWAY}/fraud/stream`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const incoming = {
        id: data.id,
        amount: data.amount,
        score: Number(data.risk_score ?? data.prediction_score ?? 0),
        decision: data.decision,
        risk_category: data.risk_category,
      };

      setTransactions((prev) => {
        const combined = [incoming, ...prev];
        const seen = new Set();
        const unique = [];
        for (const tx of combined) {
          if (!seen.has(tx.id)) {
            seen.add(tx.id);
            unique.push(tx);
          }
        }
        return unique.slice(0, 50);
      });
    };

    return () => eventSource.close();
  }, []);
  const showModal = (record) => {
    setSelectedTx(record);
    setIsModalVisible(true);
  };

  const handleOk = () => {
    setIsModalVisible(false);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
  };

  const columns = [
    {
      title: "Transaction ID",
      dataIndex: "id",
      key: "id",
      render: (text) => (
        <span style={{ fontWeight: 500, color: "#1677ff", cursor: "pointer" }}>
          {text}
        </span>
      ),
    },
    {
      title: "Amount",
      dataIndex: "amount",
      key: "amount",
      render: (amount) => `₹${amount.toFixed(2)}`,
      sorter: (a, b) => a.amount - b.amount,
    },
    {
      title: "Fraud Score",
      dataIndex: "score",
      key: "score",
      render: (score) => {
        let color = "green";
        let text = "Low Risk";
        if (score > 0.8) {
          color = "red";
          text = "High Risk";
        } else if (score > 0.4) {
          color = "orange";
          text = "Medium Risk";
        }

        return (
          <Tag color={color} style={{ width: 100, textAlign: "center" }}>
            {text} ({score.toFixed(2)})
          </Tag>
        );
      },
      sorter: (a, b) => a.score - b.score,
    },
    {
      title: "Decision",
      dataIndex: "decision",
      key: "decision",
      render: (decision) => {
        if (!decision) return null;
        let color = "default";
        let label = decision;
        if (decision === "DECLINE") {
          color = "red";
          label = "Blocked";
        } else if (decision === "REVIEW") {
          color = "orange";
          label = "Review";
        } else if (decision === "APPROVE") {
          color = "green";
          label = "Approved";
        }
        return (
          <Tag color={color} style={{ width: 100, textAlign: "center" }}>
            {label}
          </Tag>
        );
      },
    },
    {
      title: "Action",
      key: "action",
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<Search size={14} />}
          onClick={(e) => {
            e.stopPropagation();
            showModal(record);
          }}
        >
          Details
        </Button>
      ),
    },
  ];

  // Calculate stats
  const totalVolume = transactions.reduce((acc, curr) => acc + curr.amount, 0);
  const highRiskCount = transactions.filter((t) => t.score > 0.8).length;
  const dist = metrics?.distribution || { high: 0, medium: 0, low: 0 };
  const totalEvents = metrics?.total_events || 0;

  return (
    <div style={{ padding: "24px" }}>
      <div
        style={{
          marginBottom: 24,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Title level={2} style={{ margin: 0 }}>
          Transaction Overview
        </Title>
        <Button
          type="primary"
          icon={<RefreshCw size={16} style={{ marginRight: 8 }} />}
          onClick={fetchTransactions}
          loading={loading}
        >
          Refresh Data
        </Button>
      </div>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card
            bordered={false}
            style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
          >
            <Statistic
              title="Total Volume"
              value={totalVolume}
              precision={2}
              valueStyle={{ color: "#3f8600" }}
              prefix="₹"
              suffix={<Activity size={20} style={{ marginLeft: 8 }} />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card
            bordered={false}
            style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
          >
            <Statistic
              title="High Risk Transactions"
              value={highRiskCount}
              valueStyle={{ color: "#cf1322" }}
              prefix={<AlertTriangle size={20} style={{ marginRight: 8 }} />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card
            bordered={false}
            style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}
          >
            <Statistic
              title="Total Transactions"
              value={transactions.length}
              prefix={<CreditCard size={20} style={{ marginRight: 8 }} />}
            />
          </Card>
        </Col>
      </Row>

      {metrics && metrics.distribution && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={12}>
            <Card bordered={false} title="Streaming Metrics" size="small">
              <Descriptions size="small" column={1} bordered>
                <Descriptions.Item label="Events Buffered">
                  {totalEvents}
                </Descriptions.Item>
                <Descriptions.Item label="Avg Prediction Score">
                  {metrics.avg_prediction_score}
                </Descriptions.Item>
                <Descriptions.Item label="High / Medium / Low">
                  {dist.high} / {dist.medium} / {dist.low}
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>
          <Col span={12}>
            <Card bordered={false} title="Risk Distribution" size="small">
              <div
                style={{ display: "flex", flexDirection: "column", gap: 12 }}
              >
                <div>
                  <span style={{ fontSize: 12 }}>High Risk</span>
                  <Progress
                    percent={totalEvents ? (dist.high / totalEvents) * 100 : 0}
                    status="exception"
                    strokeColor="#cf1322"
                  />
                </div>
                <div>
                  <span style={{ fontSize: 12 }}>Medium Risk</span>
                  <Progress
                    percent={
                      totalEvents ? (dist.medium / totalEvents) * 100 : 0
                    }
                    strokeColor="#faad14"
                  />
                </div>
                <div>
                  <span style={{ fontSize: 12 }}>Low Risk</span>
                  <Progress
                    percent={totalEvents ? (dist.low / totalEvents) * 100 : 0}
                    strokeColor="#52c41a"
                  />
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      <Card bordered={false} style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}>
        <Table
          dataSource={transactions}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          onRow={(record) => ({
            onClick: () => showModal(record),
            style: { cursor: "pointer" },
          })}
        />
      </Card>

      <Modal
        title="Transaction Details"
        open={isModalVisible}
        onOk={handleOk}
        onCancel={handleCancel}
        footer={[
          <Button key="back" onClick={handleCancel}>
            Close
          </Button>,
          <Button key="submit" type="primary" onClick={handleOk}>
            Acknowledge
          </Button>,
        ]}
      >
        {selectedTx && (
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Transaction ID">
              {selectedTx.id}
            </Descriptions.Item>
            <Descriptions.Item label="Amount">
              ₹{selectedTx.amount.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="Risk Score">
              <Badge
                status={
                  selectedTx.score > 0.8
                    ? "error"
                    : selectedTx.score > 0.4
                      ? "warning"
                      : "success"
                }
                text={`${selectedTx.score.toFixed(4)} (${
                  selectedTx.score > 0.8
                    ? "High"
                    : selectedTx.score > 0.4
                      ? "Medium"
                      : "Low"
                })`}
              />
            </Descriptions.Item>
            <Descriptions.Item label="Timestamp">
              {new Date().toLocaleString()}
            </Descriptions.Item>
            <Descriptions.Item label="Status">
              {selectedTx.score > 0.8 ? "Flagged for Review" : "Cleared"}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
}
