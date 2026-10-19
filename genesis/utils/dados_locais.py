def funcionarios_para_garantir(context) -> list[dict]:
    funcionarios = list(context.blueprint.get("funcionarios") or [])
    local = context.runtime_config.get("funcionario_local") or []

    if not isinstance(local, list):
        raise TypeError("'funcionario_local' deve ser uma lista.")

    funcionarios.extend(local)

    vistos = set()
    resultado = []

    for funcionario in funcionarios:
        matricula = funcionario.get("matricula")
        if not matricula or matricula in vistos:
            continue

        vistos.add(matricula)
        resultado.append(funcionario)

    return resultado


def usuarios_para_garantir(context) -> list[dict]:
    usuarios = list(context.blueprint.get("usuarios") or [])
    local = context.runtime_config.get("usuario_local") or []

    if not isinstance(local, list):
        raise TypeError("'usuario_local' deve ser uma lista.")

    usuarios.extend(local)

    vistos = set()
    resultado = []

    for usuario in usuarios:
        nome = usuario.get("nome")
        if not nome or nome in vistos:
            continue

        vistos.add(nome)
        resultado.append(usuario)

    return resultado
