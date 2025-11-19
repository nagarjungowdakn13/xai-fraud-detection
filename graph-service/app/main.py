from flask import Flask, request, jsonify
from py2neo import Graph
import os

app = Flask(__name__)

# Neo4j connection
graph = Graph(
    os.getenv('NEO4J_URI', 'bolt://neo4j:7687'),
    auth=(os.getenv('NEO4J_USER', 'neo4j'), os.getenv('NEO4J_PASSWORD', 'password'))
)

@app.route('/api/graph/query', methods=['POST'])
def query():
    data = request.get_json()
    cypher_query = data['query']
    result = graph.run(cypher_query).data()
    return jsonify(result)

@app.route('/api/graph/fraud-rings', methods=['GET'])
def detect_fraud_rings():
    # Example query to detect fraud rings
    query = """
    MATCH (u:User)-[:MADE_TRANSACTION]->(m:Merchant)
    WITH u, count(m) as num_merchants
    WHERE num_merchants > 5
    RETURN u.id, num_merchants
    """
    result = graph.run(query).data()
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)