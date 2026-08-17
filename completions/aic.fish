# Fish completions for ai-git-committer
# Commands: aic, ai-git-committer

# Disable file/path completions.
complete -c aic -c ai-git-committer -f

# -------------------------------------------------------------------
# General options
# -------------------------------------------------------------------

complete -c aic -c ai-git-committer \
    -s h -l help \
    -d 'Show help message and exit'

complete -c aic -c ai-git-committer \
    -s v -l version \
    -d "Show program's version and exit"

complete -c aic -c ai-git-committer \
    -l debug \
    -d 'Enable verbose debug logging output'

# -------------------------------------------------------------------
# API key
# -------------------------------------------------------------------

complete -c aic -c ai-git-committer \
    -l api-key \
    -r \
    -d 'Encrypt and store your Groq API key securely'

# -------------------------------------------------------------------
# Model selection
# -------------------------------------------------------------------

complete -c aic -c ai-git-committer \
    -l model \
    -r \
    -a 'normal' \
    -d 'Fast and lightweight model for routine commit messages'

complete -c aic -c ai-git-committer \
    -l model \
    -r \
    -a 'smart' \
    -d 'High-capability reasoning model for complex changes'

complete -c aic -c ai-git-committer \
    -l model \
    -r \
    -a 'gpt-oss-20b' \
    -d 'Fast open-weight reasoning model'

complete -c aic -c ai-git-committer \
    -l model \
    -r \
    -a 'gpt-oss-120b' \
    -d 'Large open-weight reasoning model'

complete -c aic -c ai-git-committer \
    -l model \
    -r \
    -a 'qwen3-32b' \
    -d 'General-purpose Qwen reasoning and coding model'

complete -c aic -c ai-git-committer \
    -l model \
    -r \
    -a 'qwen3-72b' \
    -d 'Large Qwen model for demanding reasoning and coding'

complete -c aic -c ai-git-committer \
    -l model \
    -r \
    -a 'kimi-k2-instruct' \
    -d 'Large instruction-following model with strong coding capabilities'

complete -c aic -c ai-git-committer \
    -l set-model \
    -r \
    -a 'normal' \
    -d 'Set default model to normal'

complete -c aic -c ai-git-committer \
    -l set-model \
    -r \
    -a 'smart' \
    -d 'Set default model to smart'

complete -c aic -c ai-git-committer \
    -l set-model \
    -r \
    -a 'gpt-oss-20b' \
    -d 'Set default model to GPT-OSS 20B'

complete -c aic -c ai-git-committer \
    -l set-model \
    -r \
    -a 'gpt-oss-120b' \
    -d 'Set default model to GPT-OSS 120B'

complete -c aic -c ai-git-committer \
    -l set-model \
    -r \
    -a 'qwen3-32b' \
    -d 'Set default model to Qwen3 32B'

complete -c aic -c ai-git-committer \
    -l set-model \
    -r \
    -a 'qwen3-72b' \
    -d 'Set default model to Qwen3 72B'

complete -c aic -c ai-git-committer \
    -l set-model \
    -r \
    -a 'kimi-k2-instruct' \
    -d 'Set default model to Kimi K2 Instruct'

# -------------------------------------------------------------------
# Model and history information
# -------------------------------------------------------------------

complete -c aic -c ai-git-committer \
    -l list \
    -d 'List available Groq model presets and active configuration'

complete -c aic -c ai-git-committer \
    -l history \
    -d 'Display recorded commit message history'

complete -c aic -c ai-git-committer \
    -l history-clear \
    -d 'Clear all entries from history log'

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

complete -c aic -c ai-git-committer \
    -l config \
    -d 'Show active configuration settings and file paths'

complete -c aic -c ai-git-committer \
    -l edit-config \
    -d 'Open config.json in the system editor'

complete -c aic -c ai-git-committer \
    -l reset-config \
    -d 'Reset config.json to factory default values'

# -------------------------------------------------------------------
# Uninstallation
# -------------------------------------------------------------------

complete -c aic -c ai-git-committer \
    -l uninstall \
    -d 'Uninstall ai-git-committer launchers and package'

complete -c aic -c ai-git-committer \
    -l purge \
    -n '__fish_seen_argument --uninstall' \
    -d 'Also remove the configuration directory'