# EKS Setup Project

Amazon Elastic Kubernetes Service (EKS) cluster configuration using `eksctl`.

## Prerequisites

- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) configured with appropriate credentials
- [eksctl](https://eksctl.io/installation/) v0.170+
- [kubectl](https://kubernetes.io/docs/tasks/tools/) v1.29+
- IAM user/role with permissions to create EKS clusters, VPCs, and IAM roles

## Project Structure

```
eks-setup/
├── eks-cluster.yaml                          # Main EKS cluster definition (eksctl ClusterConfig)
├── logging/
│   ├── namespace.yaml                        # amazon-cloudwatch namespace
│   ├── fluent-bit-cluster-info.yaml          # Cluster metadata for Fluent Bit
│   ├── fluent-bit-configmap.yaml             # Fluent Bit pipeline configuration
│   ├── fluent-bit-daemonset.yaml             # Fluent Bit DaemonSet (log collector)
│   ├── cloudwatch-agent-configmap.yaml       # CloudWatch Agent configuration
│   ├── cloudwatch-agent-daemonset.yaml       # CloudWatch Agent DaemonSet (metrics + insights)
│   └── deploy-logging.sh                     # One-command logging stack deployment
└── README.md
```

## Cluster Overview

| Property          | Value              |
|-------------------|--------------------|
| Cluster Name      | my-eks-cluster     |
| Region            | us-east-1          |
| Kubernetes Version| 1.29               |
| VPC CIDR          | 10.0.0.0/16        |
| Node Groups       | 2 (standard + spot)|

### Node Groups

- **ng-standard** — 2 × `t3.medium` on-demand instances (scales 1–4)
- **ng-spot** — 2 × mixed spot instances (`t3.medium`, `t3.large`, `t3a.medium`, scales 0–6)

### Addons

- `vpc-cni` — VPC networking for pods
- `coredns` — Cluster DNS
- `kube-proxy` — Network proxy
- `aws-ebs-csi-driver` — EBS volume support
- `amazon-cloudwatch-observability` — CloudWatch Container Insights

## Usage

### Create the Cluster

```bash
eksctl create cluster -f eks-cluster.yaml
```

### Verify the Cluster

```bash
kubectl get nodes
kubectl get pods -A
```

### Update kubeconfig

```bash
aws eks update-kubeconfig --region us-east-1 --name my-eks-cluster
```

### Scale a Node Group

```bash
eksctl scale nodegroup --cluster my-eks-cluster --name ng-standard --nodes 3
```

### Delete the Cluster

```bash
eksctl delete cluster -f eks-cluster.yaml --disable-nodegroup-eviction
```

## Logging & Monitoring

The cluster includes a full logging stack that ships logs to **Amazon CloudWatch Logs**.

### Architecture

| Component | Role |
|-----------|------|
| **Fluent Bit** (DaemonSet) | Collects container, dataplane, and host logs from every node |
| **CloudWatch Agent** (DaemonSet) | Collects metrics and enables Enhanced Container Insights |
| **CloudWatch Control Plane Logging** | API server, audit, authenticator, controller manager, scheduler logs |
| **CloudWatch Observability Addon** | Native EKS addon for integrated observability |

### CloudWatch Log Groups

| Log Group | Contents | Retention |
|-----------|----------|-----------|
| `/aws/eks/my-eks-cluster/application` | Application container logs | 30 days |
| `/aws/eks/my-eks-cluster/dataplane` | kubelet, kube-proxy, aws-node logs | 30 days |
| `/aws/eks/my-eks-cluster/host` | Host-level dmesg and system messages | 30 days |
| `/aws/eks/my-eks-cluster/cluster` | Control plane logs (API, audit, etc.) | 30 days |

### Deploy Logging Stack

After the cluster is running, deploy the logging components:

```bash
chmod +x logging/deploy-logging.sh
./logging/deploy-logging.sh my-eks-cluster us-east-1
```

Or apply manually:

```bash
kubectl apply -f logging/namespace.yaml
kubectl apply -f logging/fluent-bit-cluster-info.yaml
kubectl apply -f logging/fluent-bit-configmap.yaml
kubectl apply -f logging/fluent-bit-daemonset.yaml
kubectl apply -f logging/cloudwatch-agent-configmap.yaml
kubectl apply -f logging/cloudwatch-agent-daemonset.yaml
```

### Verify Logging

```bash
kubectl get pods -n amazon-cloudwatch
kubectl logs -n amazon-cloudwatch -l app.kubernetes.io/name=fluent-bit --tail=20
kubectl logs -n amazon-cloudwatch -l app.kubernetes.io/name=cloudwatch-agent --tail=20
```

### View Logs in AWS Console

1. Open **CloudWatch** > **Log groups** in the AWS Console
2. Filter by `/aws/eks/my-eks-cluster/`
3. Use **CloudWatch Logs Insights** to query across log groups:

```
fields @timestamp, @message, kubernetes.namespace_name, kubernetes.pod_name
| filter kubernetes.namespace_name = "default"
| sort @timestamp desc
| limit 100
```

## Customization

Edit `eks-cluster.yaml` to change:

- **Region / AZs** — Update `metadata.region` and `availabilityZones`
- **Instance types** — Modify `instanceType` / `instanceTypes` under node groups
- **Scaling** — Adjust `minSize`, `maxSize`, `desiredCapacity`
- **Cluster version** — Change `metadata.version`
- **Log retention** — Adjust `log_retention_days` in `fluent-bit-configmap.yaml` and `logRetentionInDays` in `eks-cluster.yaml`
- **Log groups** — Change `log_group_name` in the Fluent Bit output sections
