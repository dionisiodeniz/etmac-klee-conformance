#/bin/bash
nix-shell -p klee --run "klee ${1}.bc"
