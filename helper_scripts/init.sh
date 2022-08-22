#!/bin/sh

mkdir -p .git/hooks || sudo -p mkdir .git/hooks
cp -R ./.hooks/* ./.git/hooks/

chmod +x ./.git/hooks/commit-msg
