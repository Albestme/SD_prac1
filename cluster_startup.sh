#!/bin/bash

# Clean up previous containers
docker-compose down --remove-orphans

# Start the Redis nodes
docker-compose up -d

# Wait for nodes to start
echo "Waiting for Redis nodes to start..."
sleep 15

# Create the cluster
echo "Creating Redis Cluster..."
docker exec -it redis-node1 redis-cli --cluster create \
  redis-node1:6379 \
  redis-node2:6379 \
  redis-node3:6379 \
  --cluster-replicas 0 \
  --cluster-yes

echo "Cluster setup complete!"
echo "To verify cluster status: docker exec -it redis-node1 redis-cli cluster nodes"