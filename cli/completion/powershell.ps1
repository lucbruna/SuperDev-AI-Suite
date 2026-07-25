# SuperDev CLI PowerShell completion

Register-ArgumentCompleter -Native -CommandName 'superdev' -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $commands = @(
        'init', 'dev', 'build', 'test', 'lint',
        'login', 'logout', 'whoami',
        'agent', 'workflow', 'plugin', 'ai',
        'runtime', 'deploy', 'status', 'version', 'doctor'
    )

    $commands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object {
        [System.Management.Automation.CompletionResult]::new(
            $_,
            $_,
            'ParameterValue',
            $_
        )
    }
}
