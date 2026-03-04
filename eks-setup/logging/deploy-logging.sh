#!/bin/bash
set -euo pipefail

CLUSTER_NAME="${1:-my-eks-cluster}"
AWS_REGION="${2:-us-east-1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Deploying EKS Logging Stack ==="
echo "Cluster: ${CLUSTER_NAME}"
echo "Region:  ${AWS_REGION}"
echo ""

echo "[1/5] Creating amazon-cloudwatch namespace..."
kubectl apply -f "${SCRIPT_DIR}/namespace.yaml"

echo "[2/5] Deploying Fluent Bit cluster info..."
kubectl apply -f "${SCRIPT_DIR}/fluent-bit-cluster-info.yaml"

echo "[3/5] Deploying Fluent Bit ConfigMap and DaemonSet..."
kubectl apply -f "${SCRIPT_DIR}/fluent-bit-configmap.yaml"
kubectl apply -f "${SCRIPT_DIR}/fluent-bit-daemonset.yaml"

echo "[4/5] Deploying CloudWatch Agent ConfigMap and DaemonSet..."
kubectl apply -f "${SCRIPT_DIR}/cloudwatch-agent-configmap.yaml"
kubectl apply -f "${SCRIPT_DIR}/cloudwatch-agent-daemonset.yaml"

echo "[5/5] Verifying deployment..."
echo ""
echo "Waiting for pods to be ready..."
kubectl -n amazon-cloudwatch rollout status daemonset/fluent-bit --timeout=120s || true
kubectl -n amazon-cloudwatch rollout status daemonset/cloudwatch-agent --timeout=120s || true

echo ""
echo "=== Logging Stack Status ==="
kubectl get pods -n amazon-cloudwatch
echo ""
echo "=== CloudWatch Log Groups ==="
echo "  /aws/eks/${CLUSTER_NAME}/application  - Application container logs"
echo "  /aws/eks/${CLUSTER_NAME}/dataplane    - Dataplane logs (kubelet, kube-proxy, aws-node)"
echo "  /aws/eks/${CLUSTER_NAME}/host          - Host-level logs (dmesg, messages)"
echo ""
echo "Deployment complete!"
