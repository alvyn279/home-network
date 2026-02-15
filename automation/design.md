# Implementation Plan - Home Assistant Deployment

## Problem Statement

Deploy Home Assistant on HP EliteDesk (192.168.0.68) using Docker Compose to provide centralized smart home control for 2-3 household members. The system must integrate with existing TP-Link Kasa devices, support local and VPN-based access, and follow established deployment patterns from the monitoring module.

## Requirements

### Core Deployment
- Docker Compose deployment in `automation/home-assistant/` directory
- Hybrid configuration management (core config in git, UI automations in volume)
- Accessible at http://192.168.0.68:8123 locally and via WireGuard VPN
- Multi-user authentication for 2-3 household members
- Automatic container restart on system reboot
- deploy.sh and update.sh scripts matching existing module patterns

### Device Integration
- TP-Link Kasa device integration with automatic discovery
- Discovery system ready for future device expansion beyond Kasa

### Future Enhancements (Phase 2)
- Prometheus metrics integration with existing monitoring stack
- Alexa/Google Assistant voice control (requires Nabu Casa subscription or manual setup)
- iPad dashboard optimization for kiosk mode
- HTTPS remote access via new public gateway module (separate project)

## Background

### Research Findings

*Content was rephrased for compliance with licensing restrictions*

1. **Network Mode**: Home Assistant heavily relies on device discovery protocols (mDNS, SSDP, UPnP). Using `network_mode: host` in Docker Compose attaches the container directly to the host network stack, preventing multicast/broadcast issues that occur with bridge networking.

2. **Privileged Mode**: Home Assistant Container requires `privileged: true` flag for proper operation according to official documentation.

3. **TP-Link Kasa Integration**: Home Assistant has built-in TP-Link integration supporting both Kasa and Tapo devices. The integration auto-discovers devices on the local network every 5 seconds. Newer Kasa devices may require TP-Link cloud credentials for initial authentication, but all communication happens locally afterward.

4. **Persistent Storage**: All configuration, automations, and historical data must be stored in a mounted volume. The standard path is `/config` inside the container. Home Assistant automatically generates configuration files on first launch when the config folder is empty.

5. **Image Tag**: Using `ghcr.io/home-assistant/home-assistant:stable` provides the latest stable release with manual update control.

6. **Voice Assistants**: Alexa and Google Assistant integration is most reliably achieved through Nabu Casa Cloud ($6.50/month), which handles secure remote access and voice assistant linking without complex network configuration. Manual setup is possible but requires exposing Home Assistant to the internet with HTTPS.

## Proposed Solution

Create separate test and production deployments to enable safe experimentation before production rollout:

**Test Instance (`test/` directory)**:
- Port 8124 for parallel testing alongside production
- Isolated config volume for test data
- Simple start.sh script with UFW rules
- Used for validating integrations and configurations via SSH

**Production Instance (`prod/` directory)**:
- Port 8123 (standard Home Assistant port)
- Full deploy.sh with UFW rules following monitoring module pattern
- update.sh for maintenance
- Clean deployment after test validation

**Common Configuration**:
- Host networking for device discovery
- Privileged mode as required by Home Assistant
- Persistent volume for configuration and data
- Timezone configuration via TZ environment variable
- Hybrid config approach: Home Assistant auto-generates initial configuration files, core settings managed through UI and stored in volume
- `.gitignore` to exclude sensitive data and entire config directory

**Workflow**:
1. Develop and test in `test/` directory on HP EliteDesk via SSH
2. Validate Kasa integration and multi-user setup
3. Once confirmed working, deploy production instance with `prod/deploy.sh`
4. Optionally tear down test instance or keep for future experimentation

## Task Breakdown

### Task 1: Create test and production infrastructure
- **Objective**: Set up complete test and production deployment files in one pass
- **Implementation**:
  - Create `automation/home-assistant/test/` directory with:
    - `docker-compose.yml` using `ghcr.io/home-assistant/home-assistant:stable`
    - `network_mode: host`, `privileged: true`, volume `./config:/config`
    - `.env.example` with `TZ=America/Los_Angeles`
    - `.gitignore` excluding `.env` and `config/`
    - `start.sh` script: load env, configure UFW port 8124, start container
  - Create `automation/home-assistant/prod/` directory with:
    - `docker-compose.yml` (identical to test)
    - `.env.example` with `TZ=America/Los_Angeles`
    - `.gitignore` excluding `.env` and `config/`
    - `deploy.sh` script: load env, configure UFW port 8123, start container
    - `update.sh` script: load env, pull latest image, restart container
  - Make all scripts executable
- **Demo**: Both test and prod directories ready for deployment
- **Checkpoint**: Push to repo, pull on HP EliteDesk

### Task 2: Test deployment and validate Kasa integration
- **Objective**: Verify Home Assistant works with existing Kasa devices
- **Implementation** (performed on HP EliteDesk):
  - Navigate to `automation/home-assistant/test/`
  - Copy `.env.example` to `.env`
  - Run `./start.sh`
  - Complete initial setup wizard at http://192.168.0.68:8124
  - Manually configure Home Assistant to use port 8124:
    - Edit `config/configuration.yaml`
    - Add `http:` section with `server_port: 8124`
    - Restart container with `docker compose restart`
  - Add TP-Link integration through UI (Settings > Devices & Services)
  - Verify Kasa device discovery
  - Test device control (turn on/off smart plug)
- **Demo**: Test instance running with Kasa devices controllable on port 8124

### Task 3: Test multi-user access
- **Objective**: Validate multi-user authentication works as expected
- **Implementation** (performed on HP EliteDesk):
  - Navigate to Settings > People in test instance
  - Create test user accounts
  - Configure appropriate permissions (admin vs user)
  - Test login with different accounts
  - Verify device control permissions
- **Demo**: Multiple users can log in and control devices in test instance

### Task 4: Deploy production instance
- **Objective**: Deploy validated configuration to production
- **Implementation** (performed on HP EliteDesk):
  - Navigate to `automation/home-assistant/prod/`
  - Copy `.env.example` to `.env`
  - Run `./deploy.sh`
  - Complete initial setup wizard at http://192.168.0.68:8123
  - Add TP-Link integration through UI
  - Verify Kasa device discovery
  - Create actual user accounts for household members
  - Test device control and multi-user access
- **Demo**: Production Home Assistant running on port 8123 with Kasa devices

### Task 5: Create comprehensive README
- **Objective**: Document both test and production deployments
- **Implementation**:
  - Create `automation/home-assistant/README.md` with:
    - Overview of test/prod split architecture
    - Prerequisites (Docker, Docker Compose)
    - Test workflow (SSH access, start.sh, port 8124 configuration)
    - Production deployment (deploy.sh, update.sh)
    - Access instructions for both instances
    - Initial setup wizard notes
    - TP-Link Kasa integration steps
    - Multi-user configuration
    - Troubleshooting section
- **Demo**: Complete documentation exists for both environments

### Task 6: Update main project README
- **Objective**: Document new module in project overview
- **Implementation**:
  - Update `/Users/alvyn/coding/q/home_cluster/README.md`
  - Add Home Assistant entry to HP EliteDesk services table
  - Move home-assistant from "Future Modules" to "Automation" section
  - Include port 8123, deployment type (Docker), and purpose
- **Demo**: Project README accurately reflects new automation module
