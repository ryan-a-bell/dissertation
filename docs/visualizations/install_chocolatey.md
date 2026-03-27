# How to Install Chocolatey (Windows)

This guide explains **what Chocolatey is**, **why you might want it**, and **how to install it safely on Windows**.

---

## What Is Chocolatey?

Chocolatey is a **package manager for Windows**.  
It allows you to install, update, and manage software from the command line instead of manually downloading installers.

Think of it like:
- `apt` on Linux
- `brew` on macOS

### Example
Instead of downloading installers manually, you can run:
```powershell
choco install git vscode python -y
```

Chocolatey will:
- Download verified installers
- Install them silently
- Add them to your system PATH
- Make future updates easy

---

## Why Use Chocolatey?

Chocolatey is especially useful if you care about:

- Reproducible environments
- Automation and scripting
- Fast machine setup
- Consistent developer tooling

It is commonly used in:
- DevOps workflows
- CI/CD pipelines
- Engineering teams
- Research and reproducible computing environments

---

## System Requirements

- Windows 10 or Windows 11
- Administrator privileges
- PowerShell (preinstalled on Windows)

---

## Step 1: Open PowerShell as Administrator

1. Open the **Start Menu**
2. Type **PowerShell**
3. Right-click **Windows PowerShell**
4. Select **Run as administrator**

You should see a window titled:
```
Administrator: Windows PowerShell
```

---

## Step 2: Allow Script Execution (Temporary)

Run the following command:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
```

This setting applies **only to the current PowerShell session**.

---

## Step 3: Install Chocolatey

Copy and paste the following command into PowerShell:

```powershell
[System.Net.ServicePointManager]::SecurityProtocol = `
  [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Installation usually takes **30–60 seconds**.

---

## Step 4: Verify Installation

Close PowerShell, open a new window, and run:

```powershell
choco --version
```

If a version number appears, Chocolatey is installed.

---

## Step 5: Install Software Using Chocolatey

Example:
```powershell
choco install gource ffmpeg -y
```

Other common tools:
```powershell
choco install git vscode python nodejs -y
```

---

## Updating Installed Software

```powershell
choco upgrade all -y
```

---

## When Not to Use Chocolatey

| Use Case | Better Tool |
|--------|-------------|
| Python libraries | pip, conda |
| Node packages | npm |
| Portable binaries | Direct download |

---

## Summary

Chocolatey is a powerful way to manage Windows software using the command line.  
It is ideal for automation, reproducibility, and developer workflows.

---

## References

- https://community.chocolatey.org
- https://docs.chocolatey.org
