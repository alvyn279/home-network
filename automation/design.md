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

Create a minimal Docker Compose deployment following the monitoring module pattern with:
- Host networking for device discovery
- Privileged mode as required by Home Assistant
- Single persistent volume for configuration and data
- Timezone configuration via TZ environment variable
- UFW firewall rules in deploy.sh
- Simple update.sh for pulling new images and restarting

Use hybrid config approach:
- Home Assistant auto-generates initial configuration files
- Core settings managed through UI and stored in volume
- `.gitignore` to exclude sensitive data and entire config directory

## Task Breakdown

### Task 1: Create project structure and Docker Compose configuration
- **Objective**: Set up directory structure, Docker Compose, and supporting files
- **Implementation**:
  - Create `automation/home-assistant/` directory
  - Create `docker-compose.yml` with:
    - Service using `ghcr.io/home-assistant/home-assistant:stable`
    - `network_mode: host` (required for device discovery)
    - `privileged: true` (required by Home Assistant)
    - Volume mount: `./config:/config`
    - Environment variable: `TZ`
    - `restart: unless-stopped`
  - Create `.env.example` with `TZ=America/Los_Angeles`
  - Create `.gitignore` to exclude `.env` and `config/` directory
- **Demo**: Docker Compose file validates with `docker compose config`

### Task 2: Create deploy.sh script
- **Objective**: Automate deployment with firewall configuration
- **Implementation**:
  - Create `deploy.sh` that:
    - Loads environment variables from `.env`
    - Configures UFW to allow port 8123
    - Runs `docker compose up -d`
    - Shows container status
  - Make script executable
  - Follow pattern from `monitoring/deploy.sh`
- **Demo**: Running `./deploy.sh` starts Home Assistant and opens firewall port

### Task 3: Create update.sh script
- **Objective**: Provide simple update mechanism for consistency across modules
- **Implementation**:
  - Create `update.sh` that:
    - Loads environment variables from `.env`
    - Pulls latest stable image
    - Recreates container with `docker compose up -d`
    - Shows updated container status
  - Make script executable
- **Demo**: Running `./update.sh` updates Home Assistant to latest stable

### Task 4: Create README with setup instructions
- **Objective**: Document deployment and configuration
- **Implementation**:
  - Create `automation/home-assistant/README.md` with:
    - Overview of deployment
    - Prerequisites (Docker, Docker Compose)
    - Setup steps (copy .env.example, run deploy.sh)
    - Access instructions (http://192.168.0.68:8123)
    - Update instructions (run update.sh)
    - Initial setup wizard notes
    - TP-Link Kasa integration steps
    - Troubleshooting section
- **Demo**: Complete documentation exists

### Task 5: Initial deployment and TP-Link Kasa integration
- **Objective**: Deploy Home Assistant and verify Kasa integration
- **Implementation**:
  - Copy `.env.example` to `.env`
  - Run `./deploy.sh`
  - Complete initial setup wizard at http://192.168.0.68:8123
  - Add TP-Link integration through UI (Settings > Devices & Services)
  - Verify Kasa device discovery
  - Test device control (turn on/off smart plug)
- **Demo**: Home Assistant running with Kasa devices controllable

### Task 6: Configure multi-user access
- **Objective**: Set up accounts for 2-3 household members
- **Implementation**:
  - Navigate to Settings > People
  - Create user accounts for household members
  - Configure appropriate permissions (admin vs user)
  - Test login with different accounts
  - Document user management in README
- **Demo**: Multiple users can log in and control devices

### Task 7: Update main project README
- **Objective**: Document new module in project overview
- **Implementation**:
  - Update `/Users/alvyn/coding/q/home_cluster/README.md`
  - Add Home Assistant entry to HP EliteDesk services table
  - Move home-assistant from "Future Modules" to "Automation" section
  - Include port 8123, deployment type (Docker), and purpose
- **Demo**: Project README accurately reflects new automation module
