# Home Network Cluster

A modular home network infrastructure project focused on reliability, automation, and scalability.

## Network Architecture

```
                    ┌─────────────────┐
                    │   Public        │
                    │   Internet      │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   ISP Modem     │◄──── Smart Plug (Power Control)
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │  Main Router    │
                    │  192.168.1.x    │
                    └─────────┬───────┘
                              │ Ethernet
                    ┌─────────▼───────┐
                    │ Secondary Router│
                    │  192.168.2.x    │
                    └─────────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐         ┌─────▼─────┐         ┌─────▼─────┐
   │Raspberry│         │   Smart   │         │  Future   │
   │   Pi    │         │   Plug    │         │ Devices   │
   │(Monitor)│         │(Control)  │         │           │
   └─────────┘         └───────────┘         └───────────┘
```

## Project Modules

### Resiliency
- **[wifi-reboot](resiliency/wifi-reboot/)** - Automatic modem power cycling for internet reliability

### Future Modules
- **storage/** - Network attached storage and backup solutions
- **monitoring/** - Network and system monitoring infrastructure  
- **automation/** - Smart home automation and control systems
- **security/** - VPN, firewall, and access control

## Core Principles

1. **Modularity** - Each component can be developed and deployed independently
2. **Reliability** - Redundant systems and automatic recovery mechanisms
3. **Scalability** - Architecture supports growth from basic to enterprise-grade
4. **Documentation** - Clear guides for setup, configuration, and troubleshooting

## Getting Started

1. Review the [networking documentation](docs/networking.md) for technical concepts
2. Start with the [wifi-reboot module](resiliency/wifi-reboot/) for basic internet reliability
3. Expand with additional modules based on your needs

## Hardware Foundation

- **Secondary Router**: Creates isolated network for control and monitoring
- **Raspberry Pi**: Runs monitoring and automation scripts
- **Smart Plugs**: Remote power control for devices
- **Network Switches**: Expand ethernet connectivity as needed

## Network Ranges

- **Main Network**: 192.168.1.x (existing home network)
- **Secondary Network**: 192.168.2.x (control and monitoring network)
- **Future VLANs**: 192.168.10.x+ (segmented networks for different purposes)

## Documentation

- **[docs/networking.md](docs/networking.md)** - Deep dive into networking concepts and router scaling
