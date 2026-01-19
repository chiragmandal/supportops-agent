# Fintech SaaS SupportOps Agent (Local AI Support Triage and Reply Assistant)

This project is a locally runnable AI assistant that helps a support team handle Fintech SaaS tickets faster and more consistently. It reads an internal knowledge base, triages incoming tickets, drafts customer ready replies with citations, and recommends routing decisions such as billing escalation or security escalation. Everything runs locally with Ollama and a local vector database, so you can test and iterate without sending data to external APIs.

## What this agent does

- Takes a support ticket as input through a Gradio UI
- Predicts category, priority, sentiment, confidence, and missing information
- Retrieves relevant policy and troubleshooting context from a local knowledge base using RAG
- Drafts a customer facing reply grounded in retrieved snippets
- Produces citations so you can trace which KB chunks were used
- Runs a QA checker pass that flags unsupported claims and risky requests
- Recommends routing such as auto reply, needs info, billing escalation, tech escalation, or security escalation
- Returns a structured JSON panel for debugging and evaluation

## Why this solves a practical business problem

- Reduces time spent reading and understanding tickets
- Reduces time spent searching internal documentation
- Produces consistent first draft responses that follow policy and tone
- Improves routing accuracy by standardizing escalation decisions
- Helps teams respond faster while staying grounded in internal knowledge

## Simple architecture diagram

```text
                 ┌───────────────────────────────┐
                 │          Gradio UI            │
                 │   Ticket input and chat view  │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │  Agent Orchestrator   │
                     │        agent.py       │
                     └───────┬───────┬───────┘
                             │       │
                             │       │
                             ▼       ▼
                  ┌────────────────┐  ┌─────────────────────┐
                  │   Triage LLM   │  │  Retriever (RAG)    │
                  │ triage.py      │  │ retrieve.py         │
                  │ ChatOllama     │  │ Chroma + embeddings │
                  └───────┬────────┘  └───────────┬─────────┘
                          │                       │
                          ▼                       ▼
                 ┌─────────────────┐     ┌───────────────────┐
                 │ Reply Writer LLM│     │ Local KB Documents│
                 │ reply.py        │     │ kb/*.md           │
                 │ ChatOllama      │     └───────────────────┘
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ QA Checker LLM. │
                 │ checker.py      │
                 │ ChatOllama      │
                 └────────┬────────┘
                          ▼
                 ┌─────────────────┐
                 │ Router          │
                 │ router.py       │
                 └────────┬────────┘
                          ▼
                 ┌───────────────────────────────┐
                 │Response + Routing + JSON Panel│
                 │ Answer, citations, debug info │
                 └───────────────────────────────┘


## Tech stack

The LLM runs locally using Ollama with the llama3.1 model.

Embeddings are generated locally using sentence transformers.

The vector database is Chroma with persistence on disk.

The UI is Gradio.

The orchestration is implemented in modular Python files so it is easy to extend or replace components.

## Repository structure

The agent folder contains the triage module, retrieval module, reply writer, checker, router, and the end to end agent runner.

The kb folder contains example internal documentation like billing policy, account access recovery, troubleshooting, and security rules.

The chroma_db folder is created automatically when you run the app. It stores the persisted vector index and should not be committed.

## Local setup

You need two things. Ollama running and a Python environment with dependencies.

### Step 1. Start Ollama

Run ollama serve in a terminal and keep it running.

Confirm it is reachable by calling the tags endpoint on localhost port 11434.

Make sure the model exists by running ollama list. If llama3.1 is missing, pull it using ollama pull llama3.1.

### Step 2. Create a fresh conda environment

Create a new conda environment and activate it.

Install the Python dependencies. If you want a reproducible setup, use pinned versions.

### Step 3. Run the app

Run python app.py from the repository root.

Gradio will print a local URL, typically http://127.0.0.1:7860.

Open it in your browser and paste a ticket.

## Example tickets to try

I was charged twice this month and I need a refund. Invoice shows two payments. customer_tier=SMB plan=monthly

Lost my 2FA phone, cannot log in. I am the admin and need urgent access.

We suspect fraudulent transactions and possible AML flag. What is happening.

## Output format

The chat response contains a customer facing answer followed by a routing decision.

A JSON panel is included showing category, priority, sentiment, confidence, missing info, citations, and checker output.

This makes the system easy to evaluate and improve.

## Metrics you can add next

This repository is structured so you can add an evaluation harness easily.

You can create a small labeled dataset of tickets and compute category accuracy and routing macro F1.

You can label which knowledge base document should be retrieved and compute retrieval recall at k.

You can measure unsupported claim rate using the checker output and show before and after improvements if you add a second draft pass.

## Safety and compliance notes

The assistant is instructed to never ask for full card numbers or full bank account details.

Security related topics like fraud suspicion, AML flags, or access tampering are routed to security escalation.

The assistant avoids revealing internal detection logic and stays grounded in the knowledge snippets.

## How to extend

Add more documents in the kb folder and re run the app to re index.

Replace routing logic in router.py with a policy table or a learned classifier.

Add tool calls such as invoice lookup or transaction status checks from a local CSV to make it feel like a real internal support tool.

Add eval scripts that generate a report and a metrics table for your README.
