# ai-git-committer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Arch Linux](https://img.shields.io/badge/Arch_Linux-CachyOS-brightgreen.svg)](https://archlinux.org/)

`ai-git-committer` is a production-quality CLI tool designed for Arch Linux, CachyOS, and Linux systems. It automatically stages changes, analyzes repository diffs using Groq's ultra-fast LLM API, enforces strict [Conventional Commits](https://www.conventionalcommits.org/), and executes commits with interactive confirmation.

---

## Features

- ⚡ **Groq AI Integration**: Blazing fast commit message generation using `llama-3.1-8b-instant` and `llama-3.3-70b-versatile`.
- 🔐 **Encrypted Key Storage**: API keys are securely encrypted using Fernet symmetric cryptography (`cryptography.fernet`). Plaintext keys are never saved.
- 📦 **Arch Linux & CachyOS Optimized**: Integrates seamlessly with system Python and AUR helpers (`paru` / `yay`).
- 🛠️ **Automatic PATH & Launcher Setup**: Installs `ai-git-committer` and `ai-committer` binaries into `~/.local/bin` and auto-configures your shell environment (`.bashrc`, `.zshrc`, `.profile`, `config.fish`).
- 🗑️ **Built-in Uninstaller**: Cleanly removes executable launchers, package installations, and shell PATH modifications.
- 📝 **Strict Conventional Commits**: Validates commit format (`feat:`, `fix:`, `docs:`, etc.) with automatic single-retry fallback logic.
- 📜 **History Tracking**: Keeps a local log of generated commits with timestamps and model metadata.
- ⚙️ **Configurable & Extensible**: Support schema migrations, interactive config editing with `$EDITOR`, custom model overrides, and temperature adjustments.

---

## Installation

### Method 1: Using Standalone Setup Installer (Recommended)

Clone the repository and run `install.py`:

```bash
git clone https://github.com/example/ai-git-committer.git
cd ai-git-committer
python install.py
```

`install.py` automatically:
- Detects Arch Linux / CachyOS & missing Python packages (`python-groq`, `python-cryptography`).
- Installs `ai-git-committer` & `ai-committer` launchers to `~/.local/bin`.
- Ensures `~/.local/bin` is added to your shell's `PATH` (`.bashrc`, `.zshrc`, `.profile`, `config.fish`).
- Initializes `~/.config/ai-git-committer/` directories and Fernet encryption keys.

### Method 2: Standard Python Package Installation

Install directly using `pip`:

```bash
pip install -e .
```

---

## Uninstallation

To completely uninstall `ai-git-committer`:

```bash
python uninstall.py
```

Or run via the CLI:
```bash
ai-git-committer --uninstall
```

To also remove configuration files, API keys, and history log, pass `--purge`:
```bash
python uninstall.py --purge
```

---

## Quick Start

1. **Set your Groq API key** (obtainable from [Groq Console](https://console.groq.com/)):

```bash
ai-git-committer --api-key gsk_your_encrypted_groq_api_key_here
```

2. **Run in any Git Repository**:

```bash
ai-git-committer
```

---

## Screenshots

<!-- SCREENSHOT PLACEHOLDER -->
![ai-git-committer CLI Preview](https://via.placeholder.com/800x400.png?text=ai-git-committer+Terminal+Interface+Preview)

---

## Usage & Commands

```
usage: ai-git-committer [-h] [-v] [--debug] [--api-key KEY] [--model MODEL]
                       [--set-model MODEL] [--list] [--history]
                       [--history-clear] [--config] [--edit-config]
                       [--reset-config]

Options:
  -h, --help           Show help message and exit
  -v, --version        Show program version and exit
  --debug              Enable verbose debug logging output

API Key Management:
  --api-key KEY        Encrypt and store your Groq API key securely

Model Presets & Overrides:
  --model MODEL        Temporarily override model for this run ('normal' | 'smart' | explicit ID)
  --set-model MODEL    Permanently set default model preset in config.json
  --list               List available Groq model presets and active configuration

History Management:
  --history            Display recorded commit message history log
  --history-clear      Clear all entries from history log file

Configuration:
  --config             Show active configuration settings and file paths
  --edit-config        Open config.json in system default text editor ($EDITOR)
  --reset-config       Reset config.json to factory default values
```

---

## Examples

### 1. Standard Commit with Default Preset (`normal`)

```bash
$ ai-git-committer
-> Generating commit message using model 'normal' (llama-3.1-8b-instant)...

Proposed Commit Message:
  feat(crypto): add Fernet encryption for API key storage

Proceed with this commit? [Y/n/e (edit)]: y
[✓] Commit successful!
```

### 2. Complex Refactor using `smart` Model (`llama-3.3-70b-versatile`)

```bash
$ ai-git-committer --model smart
-> Generating commit message using model 'smart' (llama-3.3-70b-versatile)...

Proposed Commit Message:
  refactor(git): migrate subprocess execution to safe parameter lists

Proceed with this commit? [Y/n/e (edit)]: y
```

### 3. View Commit History

```bash
$ ai-git-committer --history
--- Commit History Log ---
[2026-08-05 08:30:00 +0200] (normal) feat(config): implement schema auto-migration
[2026-08-05 08:32:15 +0200] (smart) refactor(ai): add single-retry fallback validation
```

---

## Configuration

Configuration files are located in `~/.config/ai-git-committer/`:

```
~/.config/ai-git-committer/
├── config.json      # Main configuration options
├── history.txt      # Recorded commit history log
├── api.key          # Fernet key permissions 0600
└── secrets.enc      # Encrypted Groq API key
```

### Default `config.json`:

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

## Arch Linux AUR Packaging

`ai-git-committer` is designed to be easily packaged for the Arch Linux AUR using `PKGBUILD`.

Sample PKGBUILD snippet:

```bash
pkgname=python-ai-git-committer
pkgver=0.1.0
pkgrel=1
pkgdesc="AI Conventional Commit message generator using Groq API"
arch=('any')
url="https://github.com/example/ai-git-committer"
license=('MIT')
depends=('python' 'python-groq' 'python-cryptography')
makedepends=('python-setuptools' 'python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
}
```

---

## Contributing

Contributions are welcome! Please follow these rules:
1. Ensure code formatted with **Black**.
2. Provide standard **type hints** and **docstrings** for all functions.
3. Submit tests or clean diffs following Conventional Commits format.

---

## License

Distributed under the [MIT License](LICENSE).
