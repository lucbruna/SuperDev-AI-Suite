#compdef superdev

_superdev() {
    local -a commands
    commands=(
        'init:Create a new project'
        'dev:Start development server'
        'build:Build the project'
        'test:Run tests'
        'lint:Lint the project'
        'login:Login to SuperDev'
        'logout:Logout'
        'whoami:Show current user'
        'agent:Manage agents'
        'workflow:Manage workflows'
        'plugin:Manage plugins'
        'ai:AI commands'
        'runtime:Manage runtimes'
        'deploy:Deploy to production'
        'status:Show platform status'
        'version:Show version'
        'doctor:Check system health'
    )

    _arguments -C \
        '1:command:->cmd' \
        '*::arg:->args'

    case $state in
        cmd)
            _describe 'command' commands
            ;;
        args)
            case ${words[1]} in
                agent)
                    _arguments \
                        '1:action:(list start stop logs status)' \
                        '*:agent:'
                    ;;
                workflow)
                    _arguments \
                        '1:action:(list create run delete)' \
                        '*:workflow:'
                    ;;
                plugin)
                    _arguments \
                        '1:action:(list install uninstall update)' \
                        '*:plugin:'
                    ;;
            esac
            ;;
    esac
}

_superdev "$@"
