# WooSarr Threat Model

## Overview

This document outlines the threat model for WooSarr, a Plex ↔ Discord Role Library Sync service. It identifies potential threats, their impact, and mitigations.

## Assets

1. **User Credentials**: Plex OAuth tokens, Discord bot tokens
2. **Configuration**: Library mappings, role mappings, exemptions
3. **Database**: SQLite database with user data and configuration
4. **Secrets**: Master key for encryption stored in `/config/secrets`

## Threats

### 1. Account-Linking Spoofing

**Threat**: A user claims someone else's Plex account by manipulating the OAuth flow.

**Impact**: Unauthorized access to library mappings.

**Mitigation**:
- Use Plex OAuth 2.0 with PKCE (Proof Key for Code Exchange)
- Verify the Plex user ID returned by the OAuth flow matches the expected user
- Store the Plex user ID in the database and compare on each sync

### 2. Privilege Escalation via Discord Roles

**Threat**: A user manipulates their Discord roles to gain unauthorized library access.

**Impact**: Unauthorized access to Plex libraries.

**Mitigation**:
- Only grant library access based on predefined role mappings
- Validate Discord role IDs against the configured mappings
- Use Discord's API to verify role membership before granting access

### 3. Token Theft from `/config`

**Threat**: An attacker gains access to the `/config` directory and steals tokens.

**Impact**: Compromise of Plex and Discord integrations.

**Mitigation**:
- Store tokens encrypted with a master key
- Use restrictive file permissions (600) on sensitive files
- Run the container as a non-root user
- Use Docker volumes for `/config` to isolate from the host filesystem

### 4. Database Tampering

**Threat**: An attacker modifies the SQLite database to change mappings or add users.

**Impact**: Unauthorized access or denial of service.

**Mitigation**:
- Use restrictive file permissions on the database file
- Run the container as a non-root user
- Validate database integrity on startup

### 5. Cross-Site Request Forgery (CSRF)

**Threat**: An attacker tricks a user into performing unintended actions.

**Impact**: Unauthorized changes to configuration.

**Mitigation**:
- Use CSRF tokens for state-changing requests
- Validate the Origin header on requests

### 6. Cross-Site Scripting (XSS)

**Threat**: An attacker injects malicious scripts into the web UI.

**Impact**: Session hijacking, data theft.

**Mitigation**:
- Use React's built-in XSS protection
- Validate and sanitize all user input
- Use Content Security Policy (CSP) headers

### 7. Man-in-the-Middle (MITM)

**Threat**: An attacker intercepts communication between the client and server.

**Impact**: Data theft, session hijacking.

**Mitigation**:
- Use HTTPS with TLS 1.2+
- Use strong cipher suites
- Validate SSL certificates

### 8. Denial of Service (DoS)

**Threat**: An attacker overwhelms the service with requests.

**Impact**: Service unavailability.

**Mitigation**:
- Use rate limiting on API endpoints
- Use a reverse proxy with DoS protection
- Monitor and alert on unusual traffic patterns

## Risk Assessment

| Threat | Likelihood | Impact | Risk Level |
|--------|------------|--------|------------|
| Account-Linking Spoofing | Low | High | Medium |
| Privilege Escalation | Low | High | Medium |
| Token Theft | Medium | High | High |
| Database Tampering | Low | Medium | Low |
| CSRF | Low | Medium | Low |
| XSS | Low | Medium | Low |
| MITM | Low | High | Medium |
| DoS | Medium | Medium | Medium |

## Conclusion

The WooSarr threat model identifies several potential threats, with token theft being the highest risk. Mitigations include encryption, restrictive permissions, and OAuth best practices. Regular security audits and updates are recommended to maintain the security posture.