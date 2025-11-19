-- Production PostgreSQL schema for fraud detection
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table with enhanced security
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    risk_score DECIMAL(3,2) DEFAULT 0.0,
    tier VARCHAR(20) DEFAULT 'standard',
    metadata JSONB
);

-- Transactions table with partitioning
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    merchant_id UUID NOT NULL,
    merchant_category VARCHAR(100),
    location JSONB,
    device_fingerprint VARCHAR(255),
    ip_address INET,
    status VARCHAR(20) DEFAULT 'pending',
    risk_score DECIMAL(3,2) DEFAULT 0.0,
    ml_score DECIMAL(3,2),
    graph_score DECIMAL(3,2),
    final_decision VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_by_model VARCHAR(50),
    explanation JSONB
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE transactions_2024_01 PARTITION OF transactions
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE transactions_2024_02 PARTITION OF transactions
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Fraud alerts table
CREATE TABLE fraud_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID REFERENCES transactions(id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    risk_score DECIMAL(3,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    assigned_to UUID REFERENCES users(id),
    resolution VARCHAR(50),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    evidence JSONB
);

-- Behavioral patterns table
CREATE TABLE user_behavioral_patterns (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    avg_transaction_amount DECIMAL(15,2),
    typical_transaction_hours INTEGER[],
    common_locations JSONB,
    preferred_merchants JSONB,
    transaction_frequency INTEGER DEFAULT 0,
    last_30_days_transactions INTEGER DEFAULT 0,
    last_30_days_amount DECIMAL(15,2) DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model performance tracking
CREATE TABLE model_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc_score DECIMAL(5,4),
    training_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    training_duration INTEGER,
    sample_size INTEGER,
    hyperparameters JSONB
);

-- Create indexes for performance
CREATE INDEX CONCURRENTLY idx_transactions_user_id ON transactions(user_id);
CREATE INDEX CONCURRENTLY idx_transactions_created_at ON transactions(created_at);
CREATE INDEX CONCURRENTLY idx_transactions_risk_score ON transactions(risk_score);
CREATE INDEX CONCURRENTLY idx_transactions_status ON transactions(status);
CREATE INDEX CONCURRENTLY idx_fraud_alerts_status ON fraud_alerts(status);
CREATE INDEX CONCURRENTLY idx_fraud_alerts_severity ON fraud_alerts(severity);
CREATE INDEX CONCURRENTLY idx_users_risk_score ON users(risk_score);

-- Create materialized views for analytics
CREATE MATERIALIZED VIEW mv_daily_fraud_metrics AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_transactions,
    COUNT(CASE WHEN risk_score > 0.7 THEN 1 END) as high_risk_transactions,
    COUNT(CASE WHEN final_decision = 'blocked' THEN 1 END) as blocked_transactions,
    AVG(risk_score) as avg_risk_score
FROM transactions
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at);

-- Refresh materialized view daily
CREATE OR REPLACE FUNCTION refresh_fraud_metrics()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_daily_fraud_metrics;
END;
$$ LANGUAGE plpgsql;