#!/usr/bin/env fish

# ===================================================================
# publisher.fish - Automated Release & Publication Script
#
# Steps performed:
# 1. Validates repository environment and Git branch.
# 2. Resolves target version (auto-bumps or syncs explicit version).
# 3. Automatically updates .SRCINFO, pyproject.toml, PKGBUILDs,
#    __init__.py, and README.md.
# 4. Executes the full automated test suite (pytest).
# 5. Automatically commits all updated packaging and version files.
# 6. Creates an annotated Git tag (v<version>).
# 7. Pushes the branch and tag to the remote Git repository.
# ===================================================================

function print_banner
    set_color -o cyan
    echo "=================================================="
    echo "       ai-git-committer Release Publisher        "
    echo "=================================================="
    set_color normal
end

function print_step -a message
    set_color -o blue
    echo -e "\n==> $message"
    set_color normal
end

function print_success -a message
    set_color -o green
    echo "[✓] $message"
    set_color normal
end

function print_warning -a message
    set_color -o yellow
    echo "[!] $message"
    set_color normal
end

function print_error -a message
    set_color -o red
    echo "[✗] $message" >&2
    set_color normal
end

function bump_semver -a current_ver bump_type
    set -l parts (string split '.' -- $current_ver)
    set -l major (test (count $parts) -ge 1; and echo $parts[1]; or echo 0)
    set -l minor (test (count $parts) -ge 2; and echo $parts[2]; or echo 0)
    set -l patch (test (count $parts) -ge 3; and echo $parts[3]; or echo 0)

    switch $bump_type
        case major
            set major (math $major + 1)
            set minor 0
            set patch 0
        case minor
            set minor (math $minor + 1)
            set patch 0
        case patch '*'
            set patch (math $patch + 1)
    end

    echo "$major.$minor.$patch"
end

function show_help
    echo "Usage: fish publisher.fish [OPTIONS] [VERSION | BUMP_TYPE]"
    echo ""
    echo "Options:"
    echo "  -y, --yes          Skip interactive confirmation prompts"
    echo "  --skip-tests       Skip running the pytest test suite"
    echo "  -h, --help         Show this help message and exit"
    echo ""
    echo "Arguments:"
    echo "  VERSION            Explicit version to publish (e.g. 0.2.2 or v0.2.2)"
    echo "  BUMP_TYPE          Automatic semantic bump: 'patch', 'minor', or 'major'"
    echo "                     If omitted and the current tag exists, 'patch' is auto-bumped."
end

# -------------------------------------------------------------------
# 0. Parse Command Line Arguments
# -------------------------------------------------------------------
argparse -n publisher.fish 'h/help' 'y/yes' 'skip-tests' -- $argv
if test $status -ne 0
    show_help
    exit 1
end

if set -q _flag_help
    show_help
    exit 0
end

set -l auto_confirm 0
if set -q _flag_yes
    set auto_confirm 1
end

set -l skip_tests 0
if set -q _flag_skip_tests
    set skip_tests 1
end

print_banner

# -------------------------------------------------------------------
# 1. Repository Validation
# -------------------------------------------------------------------
set -l script_dir (cd (dirname (status filename)); and pwd -P)
set -l repo_root (command git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null)

if test -z "$repo_root"; or not test -f "$repo_root/pyproject.toml"; or not test -f "$repo_root/packaging/PKGBUILD"
    print_error "publisher.fish must be run from inside the ai-git-committer repository."
    exit 1
end

cd "$repo_root"

set -l origin_url (command git config --get remote.origin.url 2>/dev/null)
if not string match -q -- '*ai-git-committer*' "$origin_url"
    print_error "Remote origin is not configured for ai-git-committer ($origin_url)."
    exit 1
end

set -l current_branch (command git branch --show-current 2>/dev/null)
if test -z "$current_branch"
    print_error "Detached HEAD state detected. Please checkout a valid branch (e.g. main)."
    exit 1
end

echo "Repository: $repo_root"
echo "Branch:     $current_branch"

# -------------------------------------------------------------------
# 2. Version Resolution & Automatic Synchronization
# -------------------------------------------------------------------
# Extract current version from pyproject.toml or PKGBUILD
set -l current_version (awk -F= '/^version *=/ {gsub(/[ "]/, "", $2); print $2; exit}' pyproject.toml)
if test -z "$current_version"
    set current_version (awk -F= '/^pkgver=/ {print $2; exit}' PKGBUILD)
end

set -l target_version ""
if test (count $argv) -ge 1
    set -l input_arg (string lower -- (string trim -- $argv[1]))
    if contains -- $input_arg patch minor major
        set target_version (bump_semver $current_version $input_arg)
        echo "Semantic bump requested: '$input_arg' ($current_version -> $target_version)"
    else
        set target_version (string replace -r '^v' '' -- $argv[1])
        echo "Explicit version requested: $target_version"
    end
else
    # Check if a tag for current version already exists in git
    set -l current_tag "v$current_version"
    if test -n (command git tag -l "$current_tag")
        set target_version (bump_semver $current_version patch)
        print_warning "Git tag $current_tag already exists. Auto-bumping patch version ($current_version -> $target_version)."
    else
        set target_version $current_version
        echo "Publishing current unreleased version: $target_version"
    end
end

if test -z "$target_version"
    print_error "Could not determine target version to publish."
    exit 1
end

set -l tag_name "v$target_version"

print_step "Updating version metadata across repository files ($target_version)..."

# 1. Update src/ai_git_committer/__init__.py
sed -i "s/__version__ = \".*\"/__version__ = \"$target_version\"/" src/ai_git_committer/__init__.py
print_success "Updated src/ai_git_committer/__init__.py -> $target_version"

# 2. Update pyproject.toml
sed -i "s/^version = \".*\"/version = \"$target_version\"/" pyproject.toml
print_success "Updated pyproject.toml -> $target_version"

# 3. Update root PKGBUILD and packaging/PKGBUILD
sed -i "s/^pkgver=.*/pkgver=$target_version/" PKGBUILD
sed -i "s/^pkgver=.*/pkgver=$target_version/" packaging/PKGBUILD
print_success "Updated PKGBUILD and packaging/PKGBUILD -> $target_version"

# 4. Update README.md tag reference
sed -i -E "s/reproducible \`v[0-9.]+\` Git source tag/reproducible \`$tag_name\` Git source tag/" README.md
print_success "Updated README.md -> $tag_name"

# 5. Automatically regenerate .SRCINFO from root PKGBUILD
if command -v makepkg >/dev/null 2>&1
    makepkg --printsrcinfo > .SRCINFO
    print_success "Regenerated .SRCINFO with version $target_version"
else
    # Fallback sed update if makepkg is not installed
    sed -i "s/pkgver = .*/pkgver = $target_version/" .SRCINFO
    sed -i -E "s/source = ai-git-committer-[0-9.]+/source = ai-git-committer-$target_version/" .SRCINFO
    sed -i -E "s/#tag=v[0-9.]*/#tag=$tag_name/" .SRCINFO
    print_success "Updated .SRCINFO -> $target_version"
end

# -------------------------------------------------------------------
# 3. Run Test Suite
# -------------------------------------------------------------------
if test $skip_tests -eq 0
    print_step "Running test suite (pytest)..."
    if not python3 -m pytest -v
        print_error "Tests failed! Aborting release."
        exit 1
    end
    print_success "All tests passed successfully."
else
    print_warning "Skipping test suite (--skip-tests passed)."
end

# -------------------------------------------------------------------
# 4. Commit Version & Packaging Changes
# -------------------------------------------------------------------
set -l git_status (command git status --porcelain)
if test -n "$git_status"
    print_step "Staging and committing updated version & packaging files..."
    command git add -A
    command git status -s

    if test $auto_confirm -eq 0
        read -l -P "Commit release changes for $tag_name? [Y/n] " confirm_commit
        if test -n "$confirm_commit"; and not contains -- (string lower -- "$confirm_commit") y yes
            print_error "Cannot publish with uncommitted changes. Aborting."
            exit 1
        end
    end

    command git commit -m "chore: release $tag_name"
    print_success "Committed release changes: 'chore: release $tag_name'"
else
    print_success "Working tree is clean."
end

# -------------------------------------------------------------------
# 5. Create Git Tag
# -------------------------------------------------------------------
print_step "Creating Git tag $tag_name..."

set -l existing_tag (command git tag -l "$tag_name")
if test -n "$existing_tag"
    set -l tag_commit (command git rev-parse -q --verify "refs/tags/$tag_name^{commit}")
    set -l head_commit (command git rev-parse -q --verify HEAD)

    if test "$tag_commit" = "$head_commit"
        print_warning "Tag $tag_name already exists and points to current HEAD."
    else
        print_error "Tag $tag_name already exists on a different commit ($tag_commit)."
        if test $auto_confirm -eq 0
            read -l -P "Overwrite tag $tag_name to point to current HEAD? [y/N] " confirm_retag
            if not contains -- (string lower -- "$confirm_retag") y yes
                print_error "Aborting publication."
                exit 1
            end
            command git tag -f -a "$tag_name" -m "Release $tag_name"
            print_success "Updated tag $tag_name to HEAD."
        else
            command git tag -f -a "$tag_name" -m "Release $tag_name"
            print_success "Updated tag $tag_name to HEAD."
        end
    end
else
    command git tag -a "$tag_name" -m "Release $tag_name"
    print_success "Created annotated tag $tag_name"
end

# -------------------------------------------------------------------
# 6. Push Branch and Tag
# -------------------------------------------------------------------
print_step "Ready to publish to remote repository ($origin_url)"
echo "Branch: $current_branch"
echo "Tag:    $tag_name"

if test $auto_confirm -eq 0
    read -l -P "Push $current_branch and $tag_name to origin? [Y/n] " confirm_push
    if test -n "$confirm_push"; and not contains -- (string lower -- "$confirm_push") y yes
        print_warning "Publication canceled by user (local commit and tag were preserved)."
        exit 0
    end
end

print_step "Pushing branch $current_branch to origin..."
if not command git push origin "$current_branch"
    print_error "Failed to push branch $current_branch to origin."
    exit 1
end
print_success "Pushed branch $current_branch"

print_step "Pushing tag $tag_name to origin..."
if not command git push origin "$tag_name"
    print_error "Failed to push tag $tag_name to origin."
    exit 1
end
print_success "Pushed tag $tag_name"

# -------------------------------------------------------------------
# 7. Summary Complete
# -------------------------------------------------------------------
set_color -o green
echo -e "\n=================================================="
echo "    Successfully published $tag_name to GitHub!    "
echo "=================================================="
set_color normal
