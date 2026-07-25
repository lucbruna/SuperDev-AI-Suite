package superdev.auth

default allow = false

# Permitir usuários autenticados
allow {
    input.user != null
    input.user.active == true
}

# Permitir API keys válidas
allow {
    input.api_key != null
    valid_api_key(input.api_key)
}

# Administradores podem acessar tudo
allow {
    input.user.role == "admin"
}

valid_api_key(key) {
    key != ""
    count(key) > 10
}
