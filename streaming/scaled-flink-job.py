from pyflink.datastream import StreamExecutionEnvironment, CheckpointingMode
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.common.time import Time
from pyflink.datastream.state import ValueStateDescriptor, ListStateDescriptor
import json
import time
from datetime import datetime, timedelta

class ScalableFraudDetectionFunction(KeyedProcessFunction):
    def __init__(self):
        self.user_state = None
        self.device_state = None
        self.window_size = timedelta(minutes=30)
    
    def open(self, runtime_context: RuntimeContext):
        # User behavior state (last 50 transactions)
        user_state_desc = ValueStateDescriptor(
            "user_behavior", 
            Types.PICKLED_BYTE_ARRAY()
        )
        self.user_state = runtime_context.get_state(user_state_desc)
        
        # Device fingerprint state
        device_state_desc = ValueStateDescriptor(
            "device_activity",
            Types.PICKLED_BYTE_ARRAY()
        )
        self.device_state = runtime_context.get_state(device_state_desc)
    
    def process_element(self, value, ctx: 'KeyedProcessFunction.Context'):
        transaction = json.loads(value)
        user_id = transaction['user_id']
        current_time = ctx.timestamp()
        
        # Get user behavior history
        user_behavior = self.user_state.value() or {
            'transactions': [],
            'total_amount_24h': 0,
            'transaction_count_24h': 0,
            'locations': set(),
            'last_updated': current_time
        }
        
        # Update user behavior
        self.update_user_behavior(user_behavior, transaction, current_time)
        
        # Calculate real-time risk factors
        risk_factors = self.calculate_risk_factors(transaction, user_behavior)
        
        # Apply machine learning model
        ml_score = self.apply_ml_model(transaction, user_behavior)
        
        # Combine risk factors
        final_score = self.combine_risk_scores(risk_factors, ml_score)
        
        # Generate alert if high risk
        if final_score > 0.8:
            alert = self.generate_fraud_alert(transaction, final_score, risk_factors)
            ctx.output(self.alert_output_tag, json.dumps(alert))
        
        # Save updated state
        self.user_state.update(user_behavior)
        
        return json.dumps({
            'transaction_id': transaction['id'],
            'user_id': user_id,
            'risk_score': final_score,
            'timestamp': current_time,
            'processed_at': time.time()
        })
    
    def update_user_behavior(self, behavior: dict, transaction: dict, timestamp: int):
        """Update user behavior with new transaction"""
        # Remove transactions older than 24 hours
        twenty_four_hours_ago = timestamp - (24 * 60 * 60 * 1000)
        behavior['transactions'] = [
            tx for tx in behavior['transactions'] 
            if tx['timestamp'] > twenty_four_hours_ago
        ]
        
        # Add new transaction
        behavior['transactions'].append({
            'amount': transaction['amount'],
            'merchant': transaction['merchant'],
            'location': transaction.get('location', {}),
            'timestamp': transaction['timestamp']
        })
        
        # Update aggregates
        behavior['total_amount_24h'] = sum(tx['amount'] for tx in behavior['transactions'])
        behavior['transaction_count_24h'] = len(behavior['transactions'])
        behavior['locations'].add(transaction.get('location', {}).get('country', 'Unknown'))
        behavior['last_updated'] = timestamp
    
    def calculate_risk_factors(self, transaction: dict, behavior: dict) -> dict:
        """Calculate multiple risk factors in real-time"""
        factors = {}
        
        # Amount-based risk
        avg_amount = behavior['total_amount_24h'] / max(behavior['transaction_count_24h'], 1)
        factors['amount_anomaly'] = min(transaction['amount'] / max(avg_amount, 1), 5.0)
        
        # Velocity risk
        factors['velocity_risk'] = min(behavior['transaction_count_24h'] / 10.0, 3.0)
        
        # Location risk
        factors['location_risk'] = len(behavior['locations']) / 5.0
        
        # Time-based risk
        transaction_time = datetime.fromtimestamp(transaction['timestamp'] / 1000).hour
        factors['time_risk'] = 1.0 if transaction_time in [0, 1, 2, 3, 4, 5] else 0.0
        
        return factors
    
    def apply_ml_model(self, transaction: dict, behavior: dict) -> float:
        """Apply lightweight ML model for real-time scoring"""
        # Simplified ML scoring - in production, this would call your ML service
        transaction_time = datetime.fromtimestamp(transaction['timestamp'] / 1000).hour / 24.0
        features = [
            transaction['amount'] / 1000.0,
            len(behavior['locations']),
            behavior['transaction_count_24h'],
            transaction_time
        ]
        
        # Simple weighted model
        weights = [0.4, 0.3, 0.2, 0.1]
        score = sum(f * w for f, w in zip(features, weights))
        
        return min(score, 1.0)
    
    def combine_risk_scores(self, factors: dict, ml_score: float) -> float:
        """Combine multiple risk factors into final score"""
        weights = {
            'amount_anomaly': 0.3,
            'velocity_risk': 0.25,
            'location_risk': 0.25,
            'time_risk': 0.1,
            'ml_score': 0.1
        }
        
        final_score = (
            factors['amount_anomaly'] * weights['amount_anomaly'] +
            factors['velocity_risk'] * weights['velocity_risk'] +
            factors['location_risk'] * weights['location_risk'] +
            factors['time_risk'] * weights['time_risk'] +
            ml_score * weights['ml_score']
        )
        
        return min(final_score, 1.0)
    
    def generate_fraud_alert(self, transaction: dict, score: float, factors: dict) -> dict:
        """Generate comprehensive fraud alert"""
        return {
            'alert_id': f"alert_{transaction['id']}_{int(time.time())}",
            'transaction': transaction,
            'risk_score': score,
            'risk_factors': factors,
            'timestamp': time.time(),
            'priority': 'HIGH' if score > 0.9 else 'MEDIUM',
            'recommended_action': self.get_recommended_action(score, factors)
        }
    
    def get_recommended_action(self, score: float, factors: dict) -> str:
        """Get recommended action based on risk score"""
        if score > 0.9:
            return "BLOCK_AND_ALERT"
        elif score > 0.7:
            return "REQUIRE_STRONG_AUTH"
        elif score > 0.5:
            return "REQUIRE_ADDITIONAL_VERIFICATION"
        else:
            return "MONITOR"

def setup_scalable_environment():
    env = StreamExecutionEnvironment.get_execution_environment()
    
    # Enable checkpointing for fault tolerance
    env.enable_checkpointing(10000)  # Checkpoint every 10 seconds
    env.get_checkpoint_config().set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
    
    # Set parallelism for scaling
    env.set_parallelism(10)  # 10 parallel instances
    
    # Kafka configuration for high throughput
    kafka_consumer = FlinkKafkaConsumer(
        'transactions',
        SimpleStringSchema(),
        {
            'bootstrap.servers': 'kafka-cluster:9092',
            'group.id': 'fraud-detection-v2',
            'auto.offset.reset': 'latest'
        }
    )
    
    kafka_producer = FlinkKafkaProducer(
        'fraud-alerts',
        SimpleStringSchema(),
        {'bootstrap.servers': 'kafka-cluster:9092'}
    )
    
    # Create processing pipeline
    transactions = env.add_source(kafka_consumer)
    
    # Key by user_id for partitioned processing
    keyed_stream = transactions.key_by(lambda x: json.loads(x)['user_id'])
    
    # Process with fraud detection
    processed_stream = keyed_stream.process(ScalableFraudDetectionFunction())
    
    # Send results to output topics
    processed_stream.add_sink(kafka_producer)
    
    return env

if __name__ == '__main__':
    env = setup_scalable_environment()
    env.execute("Scalable Fraud Detection v2.0")