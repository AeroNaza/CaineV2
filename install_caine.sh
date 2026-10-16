#!/bin/bash
set -e

BASE="$(cd "$(dirname "$0")" && pwd)"
DESTINO="$HOME/.local/share/caine"
ICONO="$HOME/.local/share/icons/caine.png"
APPS="$HOME/.local/share/applications"
ESCRITORIO="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Escritorio")"

mkdir -p "$DESTINO" "$(dirname "$ICONO")" "$APPS" "$ESCRITORIO"

cp "$BASE/dist/Caine" "$DESTINO/Caine"
chmod +x "$DESTINO/Caine"
cp "$BASE/assets/Cainelogo.png" "$ICONO"

crear_acceso() {
    cat > "$1" << EOF
[Desktop Entry]
Type=Application
Name=Caine
Comment=Asistente virtual Caine
Exec=$DESTINO/Caine
Icon=$ICONO
Terminal=false
Categories=Utility;
EOF
    chmod +x "$1"
    gio set "$1" metadata::trusted true 2>/dev/null || true
}

crear_acceso "$APPS/caine.desktop"
crear_acceso "$ESCRITORIO/caine.desktop"

update-desktop-database "$APPS" 2>/dev/null || true
echo "Caine instalado. Acceso directo creado en el escritorio y en el menú."
