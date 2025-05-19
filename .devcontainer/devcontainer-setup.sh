#!/bin/bash
export DEV_CONTAINER=1
chezmoi init --apply git@github.com:EdimarDeSa/dotfiles.git

echo "export DEV_CONTAINER=1" >>~/.zshrc
set -e

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

echo 'export PATH=$PATH:$HOME/.cargo/bin' >~/.config/.exports
