# ai-git-committer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Arch Linux](https://img.shields.io/badge/Arch_Linux-CachyOS-brightgreen.svg)](https://archlinux.org/)

`ai-git-committer` is an AI-powered CLI tool that generates high-quality Conventional Commit messages from your Git repository changes.

It automatically analyzes staged changes, creates commit messages using Groq's fast LLM API, validates the format, and commits with interactive confirmation.

Designed for Arch Linux, CachyOS, and Linux systems.

---

## Features

*  **Groq AI Integration**

  * Fast commit message generation using Groq-hosted LLM models.
  * Supports configurable model presets.

*  **Encrypted API Key Storage**

  * Groq API keys are encrypted using Fernet symmetric encryption.
  * Plaintext API keys are never stored.

*  **Arch Linux / CachyOS Optimized**

  * Native `PKGBUILD` support.
  * Works with Arch package management workflows.
  * Supports AUR-style installation.

*  **CLI Integration**

  * Installs the `aic` command launcher.
  * Integrates with normal Linux shell environments.

*  **Conventional Commit Enforcement**

  * Generates commits following Conventional Commits:

    * `feat:`
    * `fix:`
    * `docs:`
    * `refactor:`
    * `chore:`
    * and more.

*  **Commit History Tracking**

  * Stores generated commit history locally.
  * Includes timestamps and model information.

*  **Configurable**

  * Custom models.
  * Temperature settings.
  * Configuration editing.
  * History management.

---

# Installation

## Arch Linux / CachyOS (PKGBUILD)

Clone the repository:

```bash
git clone https://github.com/gnxbd4vbtm-ops/ai-git-committer.git
cd ai-git-committer
```

Build and install:

```bash
makepkg -si
```

The package will install:

* `aic`
* `ai-git-committer`

and required dependencies.

---

## Manual Python Installation

Install dependencies:

```bash
pip install build installer wheel
```

Build the package:

```bash
python -m build --wheel
```

Install:

```bash
pip install dist/*.whl
```

---

# Dependencies

Runtime dependencies:

* Python
* Git
* `python-cryptography`
* `python-groq`

For Arch Linux:

```bash
depends=(
    'python'
    'python-cryptography'
    'python-groq'
    'git'
)
```

`python-groq` is available through the Arch User Repository (AUR).

---

# Quick Start

## 1. Configure your Groq API key

Get your API key from:

https://console.groq.com/

Then:

```bash
aic --api-key gsk_your_key_here
```

The key is encrypted before storage.

---

## 2. Run inside a Git repository

```bash
cd your-project

aic
```

Example:

```
Generating commit message...

Proposed Commit Message:

feat(config): add automatic configuration migration

Proceed with this commit? [Y/n/e]:
```

---

# Commands

```
usage: aic [-h] [-v] [--debug] [--api-key KEY] [--model MODEL]
           [--set-model MODEL] [--list] [--history]
           [--history-clear] [--config]
           [--edit-config] [--reset-config]
```

## General

```
-h, --help
```

Show help.

```
-v, --version
```

Show version.

```
--debug
```

Enable debug output.

---

## API Key Management

```
--api-key KEY
```

Encrypt and store your Groq API key.

---

## Models

```
--model MODEL
```

Temporarily override the model.

```
--set-model MODEL
```

Save the default model.

```
--list
```

Show available models and configuration.

---

## History

```
--history
```

Display generated commit history.

```
--history-clear
```

Clear history.

---

## Configuration

```
--config
```

Show configuration paths.

```
--edit-config
```

Edit configuration.

```
--reset-config
```

Restore defaults.

---

# Examples

## Normal Commit

```bash
$ aic

Generating commit message...

feat(crypto): add encrypted API key storage

Proceed with this commit? [Y/n/e]: y

[✓] Commit successful
```

---

## Smart Model

```bash
$ aic --model smart
```

Uses the configured advanced model for more complex changes.

---

## View History

```bash
$ aic --history
```

Example:

```
[2026-08-05 08:30:00]
feat(config): implement schema migration

[2026-08-05 08:32:15]
refactor(ai): improve commit validation
```

---

# Configuration

Stored in:

```
~/.config/ai-git-committer/
```

Example:

```
~/.config/ai-git-committer/
├── config.json
├── history.txt
├── api.key
└── secrets.enc
```

Example configuration:

```json
{
  "config_version": 1,
  "default_model": "normal",
  "temperature": 0.2,
  "max_tokens": 100,
  "auto_add": true,
  "confirm_commit": true,
  "enforce_conventional_commits": true
}
```

---

# Arch Linux Packaging

The project includes a native `PKGBUILD`.

Current package version:

```
0.1.2
```

Example:

```bash
pkgname=ai-git-committer
pkgver=0.1.2
pkgrel=1

depends=(
    'python'
    'python-cryptography'
    'python-groq'
    'git'
)

makedepends=(
    'git'
    'python-build'
    'python-installer'
    'python-wheel'
)
```

Source builds directly from GitHub tags:

```bash
source=(
"$pkgname-$pkgver::git+https://github.com/gnxbd4vbtm-ops/ai-git-committer.git#tag=v$pkgver"
)
```

---

# Contributing

Contributions are welcome.

Please:

1. Follow Conventional Commits.
2. Use type hints.
3. Keep code formatted.
4. Include clear commit messages.

---

# License

Distributed under the MIT License.

See [LICENSE](LICENSE).
