# Repository Lineage Storytelling with Gource

This notebook is a **single, end‑to‑end workflow** to help you **communicate the story of your Git repository** using:

- Gource (animated history)
- Static branch lineage diagrams (Mermaid)
- Quantitative Git metrics
- Architecture‑style narrative commentary

It is designed so you can:
- Run it locally
- Export artifacts for slides / papers
- Reuse it across repositories

---

# Installing Chocolatey

Chocolatey is a package manager for windows applications. We will use it to install Gource and ffmpeg.

- Open Windows Powershell as an **administrator**
- Run the following

```
Set-ExecutionPolicy Bypass -Scope Process -Force
```

Followed by:

```
[System.Net.ServicePointManager]::SecurityProtocol = `
  [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

We can verify the installation by running

```
choco --version
```

If it does not show up in VSCode or otherwise, it may be necessary to add it to your path. You can set it at the administrative level like:

[[ add that here]]

Or you can set it at the user level (some installations may fail as they require admin creds)

```
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ProgramData\chocolatey\bin", [EnvironmentVariableTarget]::User)
```

Then open up an administrative powershell to run:
```
choco install gource ffmpeg -y
```

Optional upgrade of everything
```
choco upgrade all -y
```




---
# How to Use

## 0. How to Use This Notebook

1. Open this notebook **at the root of your Git repository**
2. Run cells top‑to‑bottom
3. Generated artifacts will appear in:
   ```
   docs/
     visuals/
     diagrams/
     lineage/
   ```
4. Drop outputs directly into a slide deck

---

## 1. Install Dependencies

> ⚠️ These commands are **system‑level installs**. Run once per machine.

### macOS
```bash
brew install gource ffmpeg
```

### Ubuntu / Debian
```bash
sudo apt update && sudo apt install -y gource ffmpeg
```

### Windows (Chocolatey)
```powershell
choco install gource ffmpeg
```

---

## 2. Verify You Are in a Git Repository

```python
import subprocess

def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True)

print(run("git status"))
```

If this fails, you are not in a Git repo.

---

## 3. Repository Archaeology (Extract the Signals)

### 3.1 Full Commit Timeline

```python
print(run("git log --oneline --decorate --date=short --all"))
```

Use this output to **mentally identify phases** such as:
- Initial prototype
- Major refactor
- Automation
- Evaluation / benchmarking

---

### 3.2 Branch Inventory

```python
print(run("git branch --all"))
```

Take note of:
- Long‑lived branches
- Feature / experiment branches
- Release or paper branches

---

## 4. Quantitative Evidence (Credibility Layer)

```python
metrics = {
    "total_commits": int(run("git log --oneline | wc -l").strip()),
    "contributors": run("git shortlog -sn").count("\n") + 1,
    "branches": int(run("git branch --all | wc -l").strip())
}

metrics
```

You can put these numbers directly into a slide.

---

## 5. Generate the Gource Animation (Core Artifact)

### 5.1 Prepare Output Directories

```python
import os

os.makedirs("docs/visuals", exist_ok=True)
```

---

### 5.2 Run Gource + Export MP4

> 🎯 This produces a **slide‑ready video**

```bash
gource \
  --seconds-per-day 0.4 \
  --auto-skip-seconds 1 \
  --file-idle-time 0 \
  --max-files 3000 \
  --hide mouse,progress \
  --title "Repository Evolution" \
  --background-colour 000000 \
  -1280x720 \
  --output-ppm-stream - \
| ffmpeg -y -r 60 -f image2pipe -vcodec ppm -i - \
  -vcodec libx264 -preset slow -crf 18 \
  -pix_fmt yuv420p \
  docs/visuals/repo_lineage.mp4
```

Output:
```
docs/visuals/repo_lineage.mp4
```

---

## 6. Static Branch Lineage Diagram (Mermaid)

### 6.1 Create Diagram File

```python
os.makedirs("docs/diagrams", exist_ok=True)
```

```python
mermaid = """
```mermaid
gitGraph
   commit id: \"Initial scaffold\"
   commit id: \"Exploratory spikes\"
   branch feature-core
   commit id: \"Core abstractions\"
   checkout main
   merge feature-core
   branch automation
   commit id: \"Pipelines & tooling\"
   checkout main
   merge automation
   branch evaluation
   commit id: \"Benchmarks & metrics\"
   checkout main
   merge evaluation
   commit id: \"Stabilization & release\"
```
"""

with open("docs/diagrams/repo_lineage.md", "w") as f:
    f.write(mermaid)

print("Mermaid diagram written to docs/diagrams/repo_lineage.md")
```

Render this in:
- GitHub
- VS Code
- Export PNG/SVG for slides

---

## 7. Phase Commentary (Why the Repo Evolved)

```python
os.makedirs("docs/lineage", exist_ok=True)
```

```python
phases = """
## Phase 1 – Prototype & Exploration
**Goal:** Discover viable architecture  
**Signals:** Rapid churn, experimental branches  
**Outcome:** Architecture candidates identified

## Phase 2 – Core Architecture Lock‑In
**Goal:** Stabilize abstractions  
**Signals:** Deeper directory structure, fewer files  
**Outcome:** Foundational modules established

## Phase 3 – Scaling & Automation
**Goal:** Enable repeatability  
**Signals:** Scripts, CI, pipelines  
**Outcome:** Reduced manual effort

## Phase 4 – Evaluation & Validation
**Goal:** Measure effectiveness  
**Signals:** Benchmarks, metrics, reports  
**Outcome:** Evidence‑backed conclusions
"""

with open("docs/lineage/phases.md", "w") as f:
    f.write(phases)

print("Phase commentary written to docs/lineage/phases.md")
```

---

## 8. Spoken Narrative (60‑Second Script)

> You can literally read this over the Gource video

```markdown
This repository began as an exploratory prototype, prioritizing discovery over correctness.

As viable architectural patterns emerged, development converged into a stable core, reflected by reduced churn and deeper structure.

The system then expanded through automation and tooling, enabling repeatability and scale.

Finally, benchmarking and evaluation phases validated system performance, marking the transition from prototype to engineered artifact.
```

---

## 9. Slide Deck Mapping (Drop‑In)

| Slide | Artifact |
|------|---------|
| 1 | Problem & Intent |
| 2 | Development Philosophy |
| 3 | `repo_lineage.mp4` (10–15s clip) |
| 4 | Mermaid lineage diagram |
| 5 | Phase table |
| 6 | Quantitative metrics |
| 7 | Outcome & readiness |

---

## 10. What You Now Have

✔ Animated history (emotional + intuitive)  
✔ Static lineage (executive clarity)  
✔ Commentary (intent & rationale)  
✔ Quantitative backing (credibility)  
✔ Repeatable workflow (future repos)

---

## Next Enhancements (Optional)

- Map phases to SysML / DoDAF views
- Generate paper‑ready figures
- Automate this notebook across repos
- Add tagging‑based phase markers

You now have a **systems‑engineering‑grade explanation of your repository’s evolution**.

