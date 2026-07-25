#!/bin/bash
# SuperDev CLI bash completion

_superdev_completions() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="init dev build test lint login logout whoami agent workflow plugin ai runtime deploy status version doctor"

    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "--help --version --verbose --quiet --format" -- ${cur}) )
        return 0
    fi

    COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
    return 0
}

complete -F _superdev_completions superdev
