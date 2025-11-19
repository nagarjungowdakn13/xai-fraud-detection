# In backend/app/services/intrusion_detection.py
class NetworkIntrusionXAI:
    def explain_intrusion_decision(self, network_packet):
        """XAI for network intrusion detection"""
        risk_factors = {
            'suspicious_ports': self.detect_suspicious_ports(network_packet),
            'protocol_anomalies': self.analyze_protocol_anomalies(network_packet),
            'traffic_patterns': self.detect_abnormal_traffic(network_packet),
            'geo_anomalies': self.check_geographic_anomalies(network_packet)
        }
        
        return self._generate_intrusion_explanation(risk_factors)