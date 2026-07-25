# SuperDev CLI fish completion

complete -c superdev -f

complete -c superdev -n '__fish_use_subcommand' -a init -d 'Create a new project'
complete -c superdev -n '__fish_use_subcommand' -a dev -d 'Start development server'
complete -c superdev -n '__fish_use_subcommand' -a build -d 'Build the project'
complete -c superdev -n '__fish_use_subcommand' -a test -d 'Run tests'
complete -c superdev -n '__fish_use_subcommand' -a lint -d 'Lint the project'
complete -c superdev -n '__fish_use_subcommand' -a login -d 'Login to SuperDev'
complete -c superdev -n '__fish_use_subcommand' -a logout -d 'Logout'
complete -c superdev -n '__fish_use_subcommand' -a whoami -d 'Show current user'
complete -c superdev -n '__fish_use_subcommand' -a agent -d 'Manage agents'
complete -c superdev -n '__fish_use_subcommand' -a workflow -d 'Manage workflows'
complete -c superdev -n '__fish_use_subcommand' -a plugin -d 'Manage plugins'
complete -c superdev -n '__fish_use_subcommand' -a ai -d 'AI commands'
complete -c superdev -n '__fish_use_subcommand' -a runtime -d 'Manage runtimes'
complete -c superdev -n '__fish_use_subcommand' -a deploy -d 'Deploy to production'
complete -c superdev -n '__fish_use_subcommand' -a status -d 'Show platform status'
complete -c superdev -n '__fish_use_subcommand' -a version -d 'Show version'
complete -c superdev -n '__fish_use_subcommand' -a doctor -d 'Check system health'
