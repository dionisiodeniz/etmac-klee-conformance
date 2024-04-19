#/bin/bash
nix-shell -p clang --run "clang -I /nix/store/6bs25zfs0y4x3y9illrd73k06whai530-klee-2.3/include -emit-llvm -c -g -O0 -Xclang -disable-O0-optnone ${1}.c"
