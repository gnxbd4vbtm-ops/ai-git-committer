#!/usr/bin/env fish

# Clean only package-manager artifacts; application source in src/ is never removed.
set -l script_dir (cd (dirname (status filename)); and pwd -P)
set -l repo_root (command git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null)

set -l packaging_dir "$repo_root/packaging"
if test -z "$repo_root"; or not test -f "$repo_root/pyproject.toml"; or not test -f "$packaging_dir/PKGBUILD"
    echo "Error: clean.fish must be run from the ai-git-committer repository." >&2
    exit 1
end

set -l origin_url (command git -C "$repo_root" config --get remote.origin.url 2>/dev/null)
if not string match -q -- '*ai-git-committer*' "$origin_url"
    echo "Error: refusing to clean because this is not the ai-git-committer repository." >&2
    exit 1
end

cd "$repo_root"
set -l pkgver (awk -F= '/^pkgver=/{print $2; exit}' PKGBUILD)
set -l extracted_source "$packaging_dir/src/ai-git-committer-$pkgver"

echo "Repository: $repo_root"
if pacman -Q ai-git-committer 2>/dev/null
    echo "Installed package:"
    pacman -Q ai-git-committer
else
    echo "Installed package: none"
end

read -l -P "Remove the installed package and generated package artifacts? [y/N] " confirm
if not contains -- (string lower -- "$confirm") y yes
    echo "Canceled."
    exit 0
end

if pacman -Q ai-git-committer >/dev/null 2>&1
    sudo pacman -Rns ai-git-committer
end

for artifact_dir in "$repo_root/.makepkg-build" "$packaging_dir/pkg" "$packaging_dir/src" "$packaging_dir/ai-git-committer-$pkgver"
    if test -d "$artifact_dir"
        if test -n "(git ls-files -- "$artifact_dir")"
            echo "Error: refusing to remove tracked path $artifact_dir" >&2
            exit 1
        end
        rm -rf -- "$artifact_dir"
    end
end

for artifact in "$packaging_dir"/*.pkg.tar.*
    if test -e "$artifact"
        rm -f -- "$artifact"
    end
end

sudo pacman -S --needed python python-cryptography python-groq git python-build python-installer python-wheel github-cli
pushd "$packaging_dir" >/dev/null
makepkg -Ccfsi
popd >/dev/null
pacman -Ql ai-git-committer
type -a aic
type -a ai-git-committer
