from typing import Dict, Any

def collect_snapshot() -> Dict[str, Any]:
    return {
    "security.encryption": {
        "resources": [
        {
            "id": "vol-1",
            "type": "block_volume",
            "encrypted_at_rest": True
        },
        {
            "id": "alb-1",
            "type": "load_balancer",
            "tls_policy": "TLS1.2-2019-Modern"
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 2,
        "metric_id": "security.encryption"
    },
    "db.utilization": {
        "databases": [
        {
            "id": "rds-a",
            "engine": "postgres",
            "cpu_p95": 0.52,
            "connections_p95": 0.61,
            "storage_iops_p95": 0.39
        },
        {
            "id": "azure-sql-1",
            "engine": "mssql",
            "cpu_p95": 0.12,
            "connections_p95": 0.18,
            "storage_iops_p95": 0.11
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 2,
        "metric_id": "db.utilization"
    },
    "lb.performance": {
        "load_balancers": [
        {
            "id": "alb-1",
            "lat_p50": 42,
            "lat_p95": 130,
            "lat_p99": 260,
            "r4xx": 0.018,
            "r5xx": 0.003,
            "unhealthy_minutes": 10,
            "requests": 100000
        },
        {
            "id": "appgw-1",
            "lat_p50": 55,
            "lat_p95": 150,
            "lat_p99": 280,
            "r4xx": 0.012,
            "r5xx": 0.004,
            "unhealthy_minutes": 4,
            "requests": 100000
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 2,
        "slo": {
        "p95_ms": 150,
        "p99_ms": 300,
        "max_5xx_rate": 0.01
        },
        "metric_id": "lb.performance"
    },
    "tagging.coverage": {
        "resources": [
        {
            "cloud": "aws",
            "id": "i-0a1b2c",
            "kind": "vm",
            "tags": {
            "env": "prod",
            "owner": "ml-team",
            "cost-center": "CC101",
            "service": "fraud"
            }
        },
        {
            "cloud": "gcp",
            "id": "gce-1",
            "kind": "vm",
            "tags": {
            "env": "dev",
            "owner": "data"
            }
        }
        ],
        "required_tags": [
        "env",
        "owner",
        "cost-center",
        "service"
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 2,
        "metric_id": "tagging.coverage"
    },
    "iac.coverage_drift": {
        "inventory": [
        {
            "id": "i-0a1b2c"
        },
        {
            "id": "alb-1"
        },
        {
            "id": "rds-a"
        }
        ],
        "iac_index": {
        "i-0a1b2c": True,
        "alb-1": False,
        "rds-a": True
        },
        "policy_findings": [
        {
            "id": "POL-001",
            "control": "no_public_ip_vm",
            "severity": "high",
            "resource_id": "i-9zzz",
            "status": "noncompliant"
        },
        {
            "id": "POL-002",
            "control": "nsg_no_any_any",
            "severity": "critical",
            "resource_id": "nsg-123",
            "status": "noncompliant"
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 3,
        "metric_id": "iac.coverage_drift"
    },
    "compute.utilization": {
        "instances": [
        {
            "id": "i-0a1b2c",
            "cpu_p95": 0.22,
            "mem_p95": 0.18,
            "low_util_hours_30d": 180
        },
        {
            "id": "vmss-2",
            "cpu_p95": 0.61,
            "mem_p95": 0.54,
            "low_util_hours_30d": 12
        },
        {
            "id": "gce-inst-1",
            "cpu_p95": 0.09,
            "mem_p95": 0.08,
            "low_util_hours_30d": 210
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 3,
        "metric_id": "compute.utilization"
    },
    "security.iam_risk": {
        "users": [
        {
            "name": "alice",
            "mfa_enabled": True
        },
        {
            "name": "bob",
            "mfa_enabled": False
        }
        ],
        "keys": [
        {
            "user": "alice",
            "age_days": 22
        },
        {
            "user": "service-user",
            "age_days": 190
        }
        ],
        "policies": [
        {
            "principal": "admin-group",
            "effect": "Allow",
            "actions": [
            "*"
            ],
            "resources": [
            "*"
            ]
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 5,
        "metric_id": "security.iam_risk"
    },
    "storage.efficiency": {
        "block_volumes": [
        {
            "id": "vol-1",
            "cloud": "aws",
            "size_gb": 500,
            "attached": False
        },
        {
            "id": "disk-2",
            "cloud": "azure",
            "size_gb": 256,
            "attached": True
        }
        ],
        "snapshots": [
        {
            "id": "snap-1",
            "cloud": "aws",
            "source_volume": None
        },
        {
            "id": "snap-2",
            "cloud": "gcp",
            "source_volume": "pd-3"
        }
        ],
        "objects": [
        {
            "bucket": "ml-prod",
            "key": "logs/2025/05/01.gz",
            "size": 10485760,
            "storage_class": "STANDARD",
            "last_modified": "2025-05-01T00:00:00Z"
        },
        {
            "bucket": "ml-prod",
            "key": "archive/2024/01/01.parquet",
            "size": 52428800,
            "storage_class": "STANDARD",
            "last_modified": "2024-01-01T00:00:00Z"
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 6,
        "metric_id": "storage.efficiency"
    },
    "cost.allocation_quality": {
        "cost_rows": [
        {
            "cloud": "aws",
            "service": "EC2",
            "resource_id": "i-0a1b2c",
            "cost": 123.45,
            "tags": {
            "env": "prod",
            "owner": "ml"
            }
        },
        {
            "cloud": "gcp",
            "service": "GCE",
            "resource_id": "",
            "cost": 42.1,
            "tags": {}
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 2,
        "metric_id": "cost.allocation_quality"
    },
    "scaling.effectiveness": {
        "ts_metrics": [
        {
            "ts": "2025-08-10T12:00:00Z",
            "target_cpu": 0.6,
            "actual_cpu": 0.82
        },
        {
            "ts": "2025-08-10T12:03:00Z",
            "target_cpu": 0.6,
            "actual_cpu": 0.65
        }
        ],
        "scale_events": [
        {
            "ts": "2025-08-10T12:02:00Z",
            "action": "scale_out",
            "delta": 2,
            "resource": "asg/app-prod"
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 3,
        "metric_id": "scaling.effectiveness"
    },
    "cost.idle_underutilized": {
        "cost_rows": [
        {
            "cloud": "aws",
            "service": "EC2",
            "resource_id": "i-0a1b2c",
            "cost": 123.45,
            "month": "2025-07",
            "tags": {
            "env": "prod"
            }
        }
        ],
        "instances": [
        {
            "id": "i-0a1b2c",
            "cpu_p95": 0.09,
            "mem_p95": 0.08,
            "low_util_hours_30d": 210
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 1,
        "total_cost_usd": 5000.0,
        "currency": "USD",
        "metric_id": "cost.idle_underutilized"
    },
    "security.public_exposure": {
        "network_policies": [
        {
            "id": "sg-1",
            "rule": "0.0.0.0/0:22",
            "resource_id": "i-9zzz"
        }
        ],
        "storage_acls": [
        {
            "bucket": "ml-prod",
            "public": True
        }
        ],
        "inventory": [
        {
            "id": "i-9zzz",
            "public_ip": True
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 3,
        "metric_id": "security.public_exposure"
    },
    "cost.commit_coverage": {
        "commit_inventory": [
        {
            "cloud": "aws",
            "type": "savings_plan",
            "family": "compute",
            "term_months": 12,
            "commit_usd_hour": 2.0,
            "start": "2025-04-01"
        },
        {
            "cloud": "gcp",
            "type": "cud",
            "family": "n1-standard",
            "term_months": 12,
            "commit_usd_hour": 1.5,
            "start": "2025-01-01"
        }
        ],
        "usage": [
        {
            "cloud": "aws",
            "family": "compute",
            "used_usd_hour": 1.8,
            "hours": 720
        },
        {
            "cloud": "gcp",
            "family": "n1-standard",
            "used_usd_hour": 1.1,
            "hours": 720
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 2,
        "metric_id": "cost.commit_coverage"
    },
    "security.vuln_patch": {
        "findings": [
        {
            "id": "CVE-2025-0001",
            "severity": "CRITICAL",
            "resource_id": "i-0a1b2c",
            "resolved": False
        },
        {
            "id": "CVE-2024-9999",
            "severity": "HIGH",
            "resource_id": "vmss-2",
            "resolved": True
        }
        ],
        "patch_status": {
        "agent_coverage_pct": 0.91,
        "avg_patch_age_days": 19
        },
        "window": "2025-07-20..2025-08-19",
        "sample_size": 2,
        "denominators": {
        "total_assets": 120,
        "scanned_assets": 110
        },
        "patch_sla_days": {
        "critical": 7,
        "high": 30
        },
        "metric_id": "security.vuln_patch"
    },
    "k8s.utilization": {
        "nodes": {
        "cpu_p95": 0.71,
        "mem_p95": 0.65
        },
        "pods": {
        "cpu_req_vs_used": 0.58,
        "mem_req_vs_used": 0.62
        },
        "binpack_efficiency": 0.74,
        "pending_pods_p95": 3,
        "window": "2025-07-20..2025-08-19",
        "sample_size": {
        "nodes": 10,
        "pods": 200
        },
        "metric_id": "k8s.utilization"
    },
    "availability.incidents": {
        "incidents": [
        {
            "id": "PD-abc",
            "sev": 1,
            "opened": "2025-08-10T09:00:00Z",
            "resolved": "2025-08-10T10:05:00Z"
        },
        {
            "id": "OPS-1234",
            "sev": 2,
            "opened": "2025-08-05T13:15:00Z",
            "resolved": "2025-08-05T15:00:00Z"
        }
        ],
        "slo_breaches": [
        {
            "service": "fraud-api",
            "hours": 2.4
        }
        ],
        "window": "2025-07-20..2025-08-19",
        "sample_size": 2,
        "metric_id": "availability.incidents"
    }
    }