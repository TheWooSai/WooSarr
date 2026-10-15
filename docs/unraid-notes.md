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
<?xml version="1.0"?>
<Container version="2">
    <Name>woosarr</Name>
    <Repository>ghcr.io/thewoo sai/woosarr:latest</Repository>
    <Registry></Registry>
    <Networking>bridge</Networking>
    <MyIP></MyIP>
    <Shell>sh</Shell>
    <Privileged>false</Privileged>
    <RestartPolicy>unless-stopped</RestartPolicy>
    <MemoryLimit>0</MemoryLimit>
    <MemoryReservation>0</MemoryReservation>
    <CpuPeriod>0</CpuPeriod>
    <CpuQuota>0</CpuQuota>
    <CpuShares>0</CpuShares>
    <CpuSetCpus></CpuSetCpus>
    <HostNetwork>false</HostNetwork>
    <HostPid>false</HostPid>
    <HostUts>false</HostUts>
    <PublishAllPorts>false</PublishAllPorts>
    <MapPort>
        <HostPort>2000</HostPort>
        <ContainerPort>2000</ContainerPort>
        <Protocol>tcp</Protocol>
    </MapPort>
    <Volume>
        <HostDir>/mnt/user/appdata/woosarr</HostDir>
        <ContainerDir>/config</ContainerDir>
        <Mode>rw</Mode>
    </Volume>
    <Environment>
        <Variable>
            <Name>WOOSARR_HOST</Name>
            <Value>0.0.0.0</Value>
        </Variable>
        <Variable>
            <Name>WOOSARR_PORT</Name>
            <Value>2000</Value>
        </Variable>
    </Environment>
    <ConsoleMode></ConsoleMode>
    <WebUI>http://[IP]:2000</WebUI>
    <TemplateURL>https://raw.githubusercontent.com/TheWooSai/WooSarr/main/unraid/woosarr.xml</TemplateURL>
</Container>
```

## Required Fields

| Field         | Description                                       |
| ------------- | ------------------------------------------------- |
| Name          | Container name                                    |
| Repository    | Docker image repository:tag                       |
| Networking    | Network mode (bridge, host, etc.)                 |
| RestartPolicy | Restart behavior                                  |
| MapPort       | Port mappings (HostPort, ContainerPort, Protocol) |
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
Template will be created in `unraid/woosarr.xml`.
