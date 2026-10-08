#!/bin/sh
# Build-only container. No host credentials or connector environment supplied.
set -eu
apk add --no-cache musl-dev perl make cmake
mkdir -p /cache/date-wrapper
cat > /cache/date-wrapper/date <<'DATE'
#!/bin/sh
if [ "$1" = -u ] && [ "$2" = +%Y-%m-%d ]; then
    echo wrapper-invoked >&2
    echo 2026-10-05
else
    exec /bin/date "$@"
fi
DATE
chmod +x /cache/date-wrapper/date
export PATH=/cache/date-wrapper:$PATH
export AUBE_PRIMER_PATH=/cache/empty-primer.rkyv.zst
: > "$AUBE_PRIMER_PATH"
touch -d @1791158400 "$AUBE_PRIMER_PATH"
test "$(stat -c %Y "$AUBE_PRIMER_PATH")" = 1791158400
stat "$AUBE_PRIMER_PATH" > /cache/primer.stat
sha256sum "$AUBE_PRIMER_PATH" /cache/date-wrapper/date > /cache/build-inputs.sha256
date -u +%Y-%m-%d > /cache/build-date.txt
env | LC_ALL=C sort > /cache/environment.txt
apk info -vv | LC_ALL=C sort > /cache/packages.txt
rustc -Vv > /cache/rustc.txt
cargo -V > /cache/cargo.txt
cargo build --release --locked --target x86_64-unknown-linux-musl -p aube --bin aube --target-dir /cache/aube
