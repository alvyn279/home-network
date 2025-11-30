# Home Network Cluster

A modular home network infrastructure project focused on reliability, automation, and scalability.

## System Architecture

### ISP Modem/Router (192.168.1.x)

| Service | Port | Purpose |
|---------|------|---------|
| **DHCP Server** | - | IP address assignment for home devices |
| **Internet Gateway** | - | Route traffic to/from internet |

### Secondary Router (192.168.2.x)

| Service | Port | Purpose |
|---------|------|---------|
| **DHCP Server** | - | IP assignment for cluster network |

### HP EliteDesk 800 G1 DM (192.168.2.x)

| Service | Module | Port | Application Type | Deployment Type | Purpose |
|---------|--------|------|------------------|-----------------|---------|
| **Internet Monitor** | Resiliency | - | Python - `python-kasa` | systemd | Ping tests, modem restart automation |
| **Prometheus** | Monitoring | 9090 | Python - `prometheus_client` | Docker - `prom/prometheus` | Metrics collection, time-series database |
| **Grafana** | Monitoring | 3000 | Web UI | Docker - `grafana/grafana` | Web dashboards, data visualization |
| **OpenVPN Server** | Control | 1194 | `server.conf` | Native Package | Secure remote network access |

### Smart Plugs (192.168.2.x)

| Service | Purpose |
|---------|---------|
| **Remote Power Control** | Power cycle ISP modem on internet failures |

## Project Modules

### Resiliency
- **[wifi-reboot](resiliency/wifi-reboot/)** - Automatic modem power cycling for internet reliability

### Control
- **[remote-access](control/remote-access/)** - Secure remote access to home network via OpenVPN

### Monitoring
- **[monitoring](monitoring/)** - Prometheus + Grafana infrastructure for metrics collection and visualization

### Future Modules
- **storage/** - Network attached storage and backup solutions
- **automation/** - Smart home automation and control systems
- **security/** - VPN, firewall, and access control

