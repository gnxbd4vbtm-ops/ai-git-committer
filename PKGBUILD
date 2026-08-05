# Maintainer: Byte Blast

pkgname=ai-git-committer
pkgver=0.1.1
pkgrel=1

pkgdesc="Generate Conventional Commits using Groq AI"
arch=('any')

url="https://github.com/gnxbd4vbtm-ops/ai-git-committer"
license=('MIT')

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

source=(
    "$pkgname-$pkgver::git+https://github.com/gnxbd4vbtm-ops/ai-git-committer.git#tag=v$pkgver"
)

sha256sums=(
    'SKIP'
)


prepare() {
    cd "$srcdir/$pkgname-$pkgver"

    echo "Preparing ai-git-committer..."
}


build() {
    cd "$srcdir/$pkgname-$pkgver"

    echo "Building Python wheel..."

    python -m build \
        --wheel \
        --no-isolation
}


package() {
    cd "$srcdir/$pkgname-$pkgver"


    echo "Installing Python package..."

    python -m installer \
        --destdir="$pkgdir" \
        dist/*.whl


    echo "Installing command launchers..."

    install -Dm755 \
        scripts/aic \
        "$pkgdir/usr/bin/aic"


    install -Dm755 \
        scripts/ai-git-committer \
        "$pkgdir/usr/bin/ai-git-committer"


    echo "Installing desktop entry..."

    install -Dm644 \
        ai-git-committer.desktop \
        "$pkgdir/usr/share/applications/ai-git-committer.desktop"


    echo "Installing icon..."

    install -Dm644 \
        icons/placeholder.png \
        "$pkgdir/usr/share/icons/hicolor/512x512/apps/ai-git-committer.png"
}