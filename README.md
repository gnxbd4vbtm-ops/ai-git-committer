# ai-git-committer

`ai-git-committer` is a terminal application that analyzes staged Git changes and uses Groq-hosted models to propose a one-line [Conventional Commit](https://www.conventionalcommits.org/) message. It validates the generated message before presenting it for interactive confirmation, then commits only after confirmation.

Groq API keys are stored locally using Fernet encryption rather than plaintext. Commit-message history and configuration are stored beneath `~/.config/ai-git-committer/`.

## Requirements

- Python 3.11 or later
- Git
- A Groq API key from <https://console.groq.com/>
- For Arch Linux packaging: `python`, `python-cryptography`, `python-groq`, `git`, `python-build`, `python-installer`, and `python-wheel`

## Install on Arch Linux

Clone the repository and build the package:

```bash
git clone git@github.com:gnxbd4vbtm-ops/ai-git-committer.git
cd ai-git-committer
cd packaging
makepkg -Ccfsi
```

The package installs:

- `/usr/bin/aic`
- `/usr/bin/ai-git-committer`
- `/usr/share/applications/ai-git-committer.desktop`
- `/usr/share/icons/hicolor/512x512/apps/ai-git-committer.png`

The Arch PKGBUILD lives in `packaging/` and builds from the reproducible `v0.1.6` Git source tag. Run makepkg from that directory: its generated `src/` and `pkg/` directories then remain separate from the tracked application source at the repository root. The PKGBUILD uses the system Python so an activated virtual environment cannot shadow Arch's `python-build` and `python-installer` packages.

## Configure Groq

Store an API key with either installed command:

```bash
aic --api-key gsk_your_key_here
```

The CLI encrypts the key before saving it. Display its configuration paths and active settings with:

```bash
aic --config
```

## Use it

Run the tool from a Git working tree:

```bash
aic
```

By default, configuration enables automatic staging (`git add .`), so review the working tree first. The application analyzes the staged name/status and diff, generates and validates a Conventional Commit message, and asks before committing. It makes no commit if you decline the prompt.

Useful supported options include:

```text
--api-key KEY       Encrypt and store a Groq API key
--model MODEL       Use a model for this run
--set-model MODEL   Save the default model or explicit model ID
--list              Show configured model presets
--history           Show generated-message history
--history-clear     Clear generated-message history
--config            Show configuration and paths
--edit-config       Open config.json in $EDITOR
--reset-config      Restore default configuration
--debug             Enable debug logging
--uninstall         Run the application's uninstall workflow
--purge             With --uninstall, remove its configuration directory
```

Run `aic --help` for the authoritative option list.

## Model presets

The two convenience presets are:

- `normal` → `openai/gpt-oss-20b`
- `smart` → `openai/gpt-oss-120b`

For example:

```bash
aic --model smart
aic --set-model openai/gpt-oss-20b
```

Any explicit valid Groq model ID may also be supplied with `--model` or `--set-model`; the displayed presets are conveniences, not a dynamically retrieved catalog of every Groq model.

## Desktop entry

The package adds **AI Git Committer** to the desktop application menu. It opens `aic --help` in a terminal and waits for Enter before closing, so the usage information remains readable.

## Development cleanup

Run:

```fish
./clean.fish
```

The script first asks for confirmation. It removes the installed `ai-git-committer` package and known generated package/build artifacts, reinstalls the required Arch build dependencies, performs `makepkg -Ccfsi`, and verifies the installed files and command launchers. It deliberately never removes `.git/` or the tracked application source under `src/ai_git_committer/`.

## Troubleshooting

### `model_not_found`

The configured model may be retired or unavailable to the API key. Replace retired model IDs with a current preset such as `normal` (`openai/gpt-oss-20b`) or `smart` (`openai/gpt-oss-120b`), or supply another valid Groq model ID.

### Empty response from GPT-OSS

GPT-OSS requests use low reasoning effort and disable returned reasoning for this focused commit-generation task. The client reports missing choices, messages, or content clearly, and logs the completion finish reason in debug mode when Groq provides one. If it persists, retry with `--debug` and check the model/API-key access in Groq.

### No staged changes

Stage changes manually with `git add`, or check the `auto_add` setting shown by `aic --config`.

## License

Distributed under the [MIT License](LICENSE).
