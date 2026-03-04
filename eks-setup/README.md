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
├── eks-cluster.yaml      # Main EKS cluster definition (eksctl ClusterConfig)
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

## Customization

Edit `eks-cluster.yaml` to change:

- **Region / AZs** — Update `metadata.region` and `availabilityZones`
- **Instance types** — Modify `instanceType` / `instanceTypes` under node groups
- **Scaling** — Adjust `minSize`, `maxSize`, `desiredCapacity`
- **Cluster version** — Change `metadata.version`
