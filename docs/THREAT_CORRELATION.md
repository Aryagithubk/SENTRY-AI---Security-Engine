# 🕸️ SENTRY AI - Phase 2 Threat Correlation & Event Hunting

This document details the **Phase 2 AI Threat Hunting and Event Correlation Engine** implemented in **SENTRY**.

---

## 🎯 Correlation Capabilities

Rather than investigating SIEM alerts independently, SENTRY correlates telemetry across:
- **Identity Systems**: User risk scores, Impossible Travel, Brute Force failed logins, MFA status.
- **Endpoints**: EDR health status, process execution, PowerShell base64 commands, ransomware file encryption.
- **Firewalls**: Outbound C2 beaconing traffic (Cobalt Strike / TLS 443).
- **Cloud Infrastructure**: AWS CloudTrail security group edits (`0.0.0.0/0` SSH access).
- **Threat Intelligence**: IP indicator reputation, threat actor attribution (`APT29 / Midnight Blizzard`).

---

## 🔗 Attack Chain Visual Representation

```text
🌐 C2 Threat IP (185.220.101.5)
      ↓
👤 Account Compromise (johndoe@securetech.com - Brute Force & Impossible Travel)
      ↓
💻 Device Infection (WS-FINANCE-04 - Base64 PowerShell execution)
      ↓
⚠️ Cobalt Strike C2 Beaconing (Outbound TCP 443 traffic)
      ↓
🚨 Ransomware Encryption (.locked files) & Impair Defenses (AWS SG edit)
```

---

## 📊 Composite Risk Scoring Model (0-100)

Composite Risk Score is computed dynamically:

$$\text{Composite Risk} = \min\left( (\text{User Risk} \times 0.3) + \sum \text{Alert Severities} + \text{Host Penalty}, 98 \right)$$

- **Critical Risk (85-98)**: Multi-vector attack chain involving ransomware/C2 and host compromise.
- **High Risk (70-84)**: Credential theft with impossible travel and failed logins.
- **Medium Risk (40-69)**: Isolated off-hours privileged access.
