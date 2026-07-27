# 📝 System & Agent Prompt Documentation

## 1. Global System Prompt (`system_prompt.py`)
Defines SOC Assistant persona, security guardrails, and markdown output standard.

## 2. Supervisor Agent Prompt (`supervisor_prompt.py`)
Instructs the Supervisor LLM to classify user intent into one of 5 specialized worker agents:
- `Alert Agent`
- `Identity Agent`
- `Endpoint Agent`
- `Incident Agent`
- `Reporting Agent`

## 3. Incident Agent & HITL Prompt (`incident_prompt.py`)
Enforces strict Human-in-the-Loop approval prior to executing any write/update operations in the Incident Management System.

## 4. Reporting Prompt (`reporting_prompt.py`)
Generates executive investigation reports structured into Summary, Threat Breakdown, Correlated Events, and SOC Containment Recommendations.
