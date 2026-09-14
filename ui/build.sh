#!/bin/sh
# Bundle the aiterm UI into ui/dist (plain static files; no dev server).
set -e
cd "$(dirname "$0")"
bun install --silent
mkdir -p dist
bun build src/main.ts --outdir dist --target browser --minify
cp index.html dist/index.html
cp src/style.css dist/style.css
cp node_modules/@xterm/xterm/css/xterm.css dist/xterm.css
# 갈렙바이블: 교회공동체 관리시스템(CCMS) 내장 웹앱 — 앱 origin 아래 ccms/index.html 로 서빙
mkdir -p dist/ccms
cp ../ccms/ccms-app.html dist/ccms/index.html
echo "ui/dist ready"
