# Galileo MCP Server — Create Datasets Overview

This document explains how to *create datasets* using the **Galileo MCP (Model Context Protocol) Server** — a bridge that lets your AI assistant in an IDE interact with Galileo’s platform.

---

## 🧠 What Is Galileo MCP?

The **Galileo MCP Server** connects your development environment (such as VS Code or Cursor) to Galileo’s evaluation and observability platform. Through MCP, your IDE assistant can:

- Create and manage datasets  
- Run experiments  
- Build prompt templates  
- Check dataset status  
- Access logs, traces, and evaluation insights

MCP (Model Context Protocol) provides a standardized way for LLMs to call external tools and services.

---

## 📁 What “Create Datasets” Means

In Galileo, a **dataset** is a structured collection of test cases used for experimentation or evaluation.

Each dataset row can include:

- **Input** — the prompt or context sent to the model  
- **Expected output** (optional) — ground‑truth answers for evaluation  
- **Metadata** — tags, categories, or attributes used for filtering and analysis

Datasets may be fully manual, fully synthetic, or a hybrid of both.

---

## 🔧 Creating Datasets via MCP (Natural Language)

Once the Galileo MCP Server is installed and configured in your IDE, you can create datasets using natural language instructions.

### Example Requests

```
Create a dataset with 50 customer support questions about billing issues
```

```
Generate a dataset of prompt‑injection attempts against a chatbot
```

```
Create a dataset with product recommendation queries including edge cases
```

The MCP server interprets your request and executes the dataset creation through Galileo’s backend.

---

## ⏳ Checking Dataset Status

Dataset creation may take time. You can ask your assistant:

```
Check the status of my dataset generation
```

```
Is the billing questions dataset ready yet?
```

The assistant will report progress and may provide previews of generated rows.

---

## 🆔 Dataset Completion

When finished, Galileo will return:

- A **dataset ID**  
- Confirmation that the dataset is ready for experiments or evaluation

This dataset can now be referenced in experiments, evaluations, or further processing.

---

## 🛠️ Alternative Dataset Creation Methods

While MCP focuses on conversational creation, datasets can also be created through:

### 1. Galileo Console (UI)
- Upload CSV, JSON, JSONL, or Feather files
- Manually edit rows in a table interface

### 2. Programmatic Creation (Python / TypeScript)

Example (Python):

```python
import promptquality as pq
import os

pq.login(os.environ["GALILEO_CONSOLE_URL"])

dataset = pq.create_dataset({
    "input": [
        {"virtue": "benevolence", "voice": "Oprah Winfrey"},
        {"virtue": "trustworthiness", "voice": "Barack Obama"},
    ]
})
```

This creates a simple dataset with two rows.

---

## 📌 Best Practices

- Use synthetic data to stress‑test edge cases and failure modes
- Include expected outputs if you plan to compute accuracy‑based metrics
- Use metadata fields to segment results later
- Combine MCP‑generated datasets with real production samples

---

## 🧩 Summary Table

| Capability | Description |
|----------|-------------|
| Dataset Creation | Natural‑language dataset generation via IDE assistant |
| Status Tracking | Ask the assistant for progress updates |
| Evaluation Ready | Datasets feed directly into Galileo experiments |
| Multiple Entry Points | MCP, UI, or SDK‑based creation |

---

## 🧭 Key Concepts

- **Dataset** — structured evaluation or experiment inputs
- **MCP Server** — tool interface between LLMs and Galileo
- **Natural‑Language Tooling** — request dataset creation conversationally

---

*This file is suitable for direct inclusion in a research repo, documentation folder, or experiment notebook.*

