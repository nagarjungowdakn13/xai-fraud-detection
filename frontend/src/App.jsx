import {
  Avatar,
  Badge,
  Button,
  ConfigProvider,
  Layout,
  Menu,
  Space,
  Typography,
  theme,
} from "antd";
import {
  Bell,
  Home as HomeIcon,
  LayoutDashboard,
  Menu as MenuIcon,
  ShieldAlert,
  User,
} from "lucide-react";
import { useState } from "react";
import {
  Link,
  Route,
  BrowserRouter as Router,
  Routes,
  useLocation,
} from "react-router-dom";
import Dashboard from "./pages/dashboard";
import Home from "./pages/index";

const { Header, Content, Footer, Sider } = Layout;
const { Title } = Typography;

const AppLayout = () => {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const items = [
    {
      key: "/",
      icon: <HomeIcon size={20} />,
      label: <Link to="/">Overview</Link>,
    },
    {
      key: "/dashboard",
      icon: <LayoutDashboard size={20} />,
      label: <Link to="/dashboard">Live Monitor</Link>,
    },
  ];

  return (
    <Layout style={{ minHeight: "100vh", background: "transparent" }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={(value) => setCollapsed(value)}
        width={260}
        trigger={null}
        style={{
          background: "rgba(15, 23, 42, 0.6)",
          backdropFilter: "blur(12px)",
          borderRight: "1px solid rgba(255,255,255,0.08)",
          position: "fixed",
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            height: 80,
            display: "flex",
            alignItems: "center",
            justifyContent: collapsed ? "center" : "flex-start",
            padding: collapsed ? "0" : "0 24px",
            borderBottom: "1px solid rgba(255,255,255,0.05)",
            marginBottom: 16,
          }}
        >
          <div
            style={{
              background: "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
              padding: 8,
              borderRadius: 12,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 15px rgba(59, 130, 246, 0.5)",
            }}
          >
            <ShieldAlert color="white" size={24} />
          </div>
          {!collapsed && (
            <span
              style={{
                color: "white",
                marginLeft: 16,
                fontWeight: "700",
                fontSize: 22,
                letterSpacing: "-0.5px",
                background: "linear-gradient(to right, #fff, #94a3b8)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              FraudGuard
            </span>
          )}
        </div>
        <Menu
          theme="dark"
          selectedKeys={[location.pathname]}
          mode="inline"
          items={items}
          style={{ background: "transparent", padding: "0 12px" }}
        />
      </Sider>
      <Layout
        style={{
          marginLeft: collapsed ? 80 : 260,
          transition: "all 0.2s",
          background: "transparent",
        }}
      >
        <Header
          style={{
            padding: "0 32px",
            background: "rgba(15, 23, 42, 0.6)",
            backdropFilter: "blur(12px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            height: 80,
            borderBottom: "1px solid rgba(255,255,255,0.05)",
            position: "sticky",
            top: 0,
            zIndex: 99,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <Button
              type="text"
              icon={<MenuIcon size={20} color="#94a3b8" />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ color: "#94a3b8" }}
            />
            <Title
              level={4}
              style={{
                margin: 0,
                fontWeight: 600,
                color: "#f8fafc",
                letterSpacing: "-0.5px",
              }}
            >
              {items.find((i) => i.key === location.pathname)?.label.props
                .children || "Dashboard"}
            </Title>
          </div>

          <Space size={24}>
            <Badge dot color="#ef4444" offset={[-4, 4]}>
              <Button
                type="text"
                shape="circle"
                icon={<Bell size={20} color="#94a3b8" />}
              />
            </Badge>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "6px 12px",
                background: "rgba(255,255,255,0.05)",
                borderRadius: 30,
              }}
            >
              <Avatar
                style={{
                  background:
                    "linear-gradient(135deg, #3b82f6 0%, #2dd4bf 100%)",
                }}
                icon={<User size={16} />}
              />
              <span
                style={{
                  color: "#e2e8f0",
                  fontWeight: 500,
                  fontSize: 14,
                }}
              >
                Admin User
              </span>
            </div>
          </Space>
        </Header>
        <Content
          style={{
            margin: "24px 32px",
            minHeight: 280,
            overflow: "initial",
          }}
        >
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: "#3b82f6",
          colorBgContainer: "#1e293b",
          borderRadius: 12,
          fontFamily: "'Inter', sans-serif",
          colorText: "#e2e8f0",
          colorTextSecondary: "#94a3b8",
        },
        components: {
          Menu: {
            itemSelectedBg: "rgba(59, 130, 246, 0.15)",
            itemSelectedColor: "#60a5fa",
            itemColor: "#94a3b8",
            itemHoverColor: "#f8fafc",
            itemHoverBg: "rgba(255, 255, 255, 0.05)",
            itemBorderRadius: 8,
            itemMarginInline: 0,
          },
          Card: {
            colorBgContainer: "rgba(30, 41, 59, 0.6)",
            colorBorderSecondary: "rgba(255, 255, 255, 0.08)",
          },
        },
      }}
    >
      <Router>
        <AppLayout />
      </Router>
    </ConfigProvider>
  );
}
