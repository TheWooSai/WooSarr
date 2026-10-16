# Unraid Template Requirements (P0-06)

**Date:** 2026-10-15

## Docker Container Template Format

Unraid uses XML templates for Docker containers. The template defines:

- Container name
- Image repository and tag
- Port mappings
- Volume mounts
- Environment variables
- Network mode
- Restart policy

## Template XML Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<Container>
  <Name>woosarr</Name>
  <Repository>ghcr.io/thewooSai/woosarr:latest</Repository>
  <Registry></Registry>
  <Networking>bridge</Networking>
  <Privileged>false</Privileged>
  <RestartPolicy>unless-stopped</RestartPolicy>
  <MemoryLimit>0</MemoryLimit>
  <MemorySwapLimit>0</MemorySwapLimit>
  <CpuPeriod>0</CpuPeriod>
  <CpuQuota>0</CpuQuota>
  <CpuShares>0</CpuShares>
  <CpuSetCpus></CpuSetCpus>
  <OomKillDisable>false</OomKillDisable>
  <HostNetwork>false</HostNetwork>
  <HostPID>false</HostPID>
  <HostIPC>false</HostIPC>
  <PublishAllPorts>false</PublishAllPorts>
  <PortForwarding>
    <Port>
      <HostPort>2000</HostPort>
      <ContainerPort>2000</ContainerPort>
      <Protocol>tcp</Protocol>
    </Port>
  </PortForwarding>
  <Volume>
    <HostDir>/mnt/user/appdata/woosarr</HostDir>
    <ContainerDir>/config</ContainerDir>
    <Mode>rw</Mode>
  </Volume>
  <Environment>
    <Variable>
      <Name>PUID</Name>
      <Value>99</Value>
    </Variable>
    <Variable>
      <Name>PGID</Name>
      <Value>100</Value>
    </Variable>
    <Variable>
      <Name>CONFIG_DIR</Name>
      <Value>/config</Value>
    </Variable>
  </Environment>
  <ConsoleMode></ConsoleMode>
  <WebUI>http://[IP]:[PORT:2000]</WebUI>
  <TemplateURL>https://raw.githubusercontent.com/TheWooSai/WooSarr/main/unraid/woosarr.xml</TemplateURL>
  <Icon>https://raw.githubusercontent.com/TheWooSai/WooSarr/main/unraid/icon.png</Icon>
  <Description>WooSarr - Plex &amp; Discord role-based library sync. Automatically grants/removes Plex library access based on Discord roles.</Description>
  <ExtraParams></ExtraParams>
</Container>
```

## Required Fields

| Field         | Description                                       |
| ------------- | ------------------------------------------------- |
| Name          | Container name                                    |
| Repository    | Docker image repository:tag                       |
| Networking    | Network mode (bridge, host, etc.)                 |
| RestartPolicy | Restart behavior                                  |
| PortForwarding | Port mappings (HostPort, ContainerPort, Protocol) |
| Volume        | Volume mounts (HostDir, ContainerDir, Mode)       |
| Environment   | Environment variables                             |

## Volume Mappings

- `/config` - Application data (database, secrets, logs)
- Mount point: `/mnt/user/appdata/woosarr`

## Port Mappings

- `2000:2000/tcp` - Web UI and API

## Network Configuration

- Bridge networking (default)
- Host networking optional for Plex local access

## Publishing Templates

1. Create template XML file
2. Host on GitHub repository
3. Submit to Unraid Community Applications repository
4. Template URL: `https://raw.githubusercontent.com/TheWooSai/WooSarr/main/unraid/woosarr.xml`

## Verification Result

✅ **VERIFIED:** Unraid template requirements documented.
Template created in `unraid/woosarr.xml`.
