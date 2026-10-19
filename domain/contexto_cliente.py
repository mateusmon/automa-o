"""
Este arquivo é usado no conftest.py na fixture contexto_cliente.
"""

import random


class ContextoCliente:
    """
    Representa o contexto de dados de um cliente para testes data-driven.

    Esta classe encapsula fornecedores e seus materiais, oferecendo métodos
    seguros e expressivos para seleção de dados (aleatória, por índice ou por
    quantidade), sem que os testes precisem conhecer detalhes da estrutura
    interna dos dados.

    Invariantes:
    - Fornecedores e materiais individuais são representados como dicionários,
    entretanto, o grupo é fornecido por meio de listas.
    - A ordem dos fornecedores e materiais segue a ordem definida nos dados
    de entrada.
    """

    def __init__(self, raw_data: dict):
        """
        Inicializa o contexto do cliente a partir dos dados brutos.

        Espera-se que `raw_data` contenha a chave "fornecedores", cujo valor
        seja um dicionário de fornecedores.

        :param raw_data: Dados brutos do cliente (ex: carregados de YAML)
        :type raw_data: dict
        :raises ValueError: Caso não sejam encontrados fornecedores
        """
        self._dados_cliente = raw_data.get("dados_cliente", {})
        self._credenciais_ambiente = raw_data.get("_credenciais_ambiente", {})
        self._cidade = raw_data.get("cidade", {})
        self._funcao = raw_data.get("funcao", {})
        self._unidade_medida = raw_data.get("unidade_medida", {})
        self._prefixo_perfil = raw_data.get("prefixo_perfil", "")
        self._usuarios = [
            *(raw_data.get("usuarios") or []),
            *(raw_data.get("_usuario_local") or []),
        ]
        self._ug = raw_data.get("unidade_gestora", {})
        self._urs = raw_data.get("unidades_requisicao", [])
        self._almoxarifados = raw_data.get("almoxarifados", [])
        self._fornecedores = raw_data.get("fornecedores", [])
        self._materiais = raw_data.get("materiais", [])
        self._bens = raw_data.get("bens", [])
        self._ua = raw_data.get("unidade_administrativa", {})
        self._enderecos_material = raw_data.get("enderecos_material", [])
        self._unidades_localizacao = raw_data.get("unidades_localizacao", [])
        self._unidade_localizacao_estoque = raw_data.get(
            "unidade_localizacao_estoque", {}
        )
        self._funcionarios = [
            *(raw_data.get("funcionarios") or []),
            *(raw_data.get("_funcionario_local") or []),
        ]
        self._ua_cr = raw_data.get("unidade_administrativa_cr", {})
        self._ug_cr = raw_data.get("unidade_gestora_cr", {})
        self._ur_cr = raw_data.get("unidade_requisicao_cr", {})
        self._ul_cr = raw_data.get("unidade_localizacao_cr", {})
        self._cc_cr = raw_data.get("centro_custo_cr", {})
        self._almoxarifado_cr = raw_data.get("almoxarifado_cr", {})
        self._fornecedor_cr = raw_data.get("fornecedor_cr", {})
        self._orgao_externo_cr = raw_data.get("orgao_externo_cr", {})
        self._orgao_externo = raw_data.get("orgao_externo", {})
        self._portador_cr = raw_data.get("portador_cr", {})
        self._pais_cr = raw_data.get("pais_cr", {})
        self._regiao_cr = raw_data.get("regiao_cr", {})
        self._uf_cr = raw_data.get("uf_cr", {})
        self._cidade_cr = raw_data.get("cidade_cr", {})
        self._instalacao_cr = raw_data.get("instalacao_cr", {})
        self._endereco_cr = raw_data.get("endereco_cr", {})
        self._funcao_cr = raw_data.get("funcao_cr", {})
        self._funcionario_cr = raw_data.get("funcionario_cr", {})
        self._unidade_medida_cr = raw_data.get("unidade_medida_cr", {})
        self._material_consumo_cr = raw_data.get("material_consumo_cr", {})
        self._material_permanente_cr = raw_data.get("material_permanente_cr", {})
        self._material_servico_cr = raw_data.get("material_servico_cr", {})
        self._modelo_importacao_cr = raw_data.get("modelo_importacao_cr", {})
        self._supply_cr = raw_data.get("supply_cr", {})
        self._caracteristica_bem_cr = raw_data.get("caracteristica_bem_cr", {})
        self._perfil_cr = raw_data.get("perfil_cr", {})
        self._funcionario_usuario_cr = raw_data.get("funcionario_usuario_cr", {})
        self._evento = raw_data.get("evento", {})
        self._grupos = raw_data.get("grupos", [])
        self._centro_custo = raw_data.get("centro_custo", {})
        self._instalacao = raw_data.get("instalacao", {})
        self._enderecos = raw_data.get("enderecos", [])
        self._catalogo = raw_data.get("catalogo", [])

    def dados_cliente(self) -> dict:
        """
        Retorna os dados do cliente.

        :return: Dicionário de dados do cliente
        :rtype: dict
        """
        if not self._dados_cliente:
            raise ValueError("Nenhum dado encontrado para este cliente.")

        return self._dados_cliente

    def dados_usuario(self, papel: str) -> dict:
        """Retorna URL e credenciais do papel solicitado no ambiente ativo.

        Mantém ``dados_cliente()`` compatível com os testes existentes e
        permite que cenários do Genesis escolham explicitamente usuários como
        ``link`` ou ``teste``.

        :param papel: Chave do usuário em ``ambientes.<ambiente>.usuarios``.
        :return: Cópia dos dados do cliente com usuário e senha do papel.
        :raises ValueError: Se o papel não estiver configurado.
        """
        credenciais = self._credenciais_ambiente.get(papel)
        if not credenciais:
            cliente = self._dados_cliente.get("cliente", "?")
            raise ValueError(
                f"Usuário do papel '{papel}' não configurado para o cliente '{cliente}'."
            )

        dados = dict(self._dados_cliente)
        dados["usuario"] = credenciais.get("usuario")
        dados["senha"] = credenciais.get("senha")

        if not dados["usuario"] or not dados["senha"]:
            raise ValueError(
                f"Credenciais incompletas para o papel '{papel}' no ambiente ativo."
            )

        return dados

    def usuarios(self) -> list[dict]:
        """Retorna os usuários persistentes do blueprint; ausência resulta em lista vazia."""
        return self._usuarios

    def prefixo_perfil(self, obrigatorio: bool = True) -> str:
        """Retorna o prefixo Genesis; permite ausência em rotinas que a ignoram."""
        if obrigatorio and not self._prefixo_perfil:
            raise ValueError("Nenhum 'prefixo_perfil' encontrado no blueprint.")
        return self._prefixo_perfil or ""

    def cidade(self) -> dict:
        """Retorna a Cidade persistente usada como massa-base do Genesis."""
        if not self._cidade:
            raise ValueError("Nenhuma 'cidade' encontrada no blueprint.")
        return self._cidade

    def funcao(self) -> dict:
        """Retorna a Função persistente usada como massa-base do Genesis."""
        if not self._funcao:
            raise ValueError("Nenhuma 'funcao' encontrada no blueprint.")
        return self._funcao

    def unidade_medida(self) -> dict:
        """Retorna a Unidade de Medida persistente usada como massa-base do Genesis."""
        if not self._unidade_medida:
            raise ValueError("Nenhuma 'unidade_medida' encontrada no blueprint.")
        return self._unidade_medida

    def ua(self) -> dict:
        """
        Retorna a UA.

        : return: Dicionário de UA
        : rtype: dict
        """

        if not self._ua:
            raise ValueError("Nenhuma UA encontrada para este cliente.")

        return self._ua

    def unidade_administrativa_cr(self) -> dict:
        """
        Retorna os dados da Unidade Administrativa de teste do módulo
        Corporativo (chave `unidade_administrativa_cr` do blueprint).

        :return: Dicionário com sigla, ug, nome e responsavel{nome, funcao}
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._ua_cr:
            raise ValueError(
                "Nenhuma 'unidade_administrativa_cr' encontrada no blueprint."
            )

        return self._ua_cr

    def unidade_gestora_cr(self) -> dict:
        """
        Retorna os dados da Unidade Gestora de teste do módulo Corporativo
        (chave `unidade_gestora_cr` do blueprint).

        :return: Dicionário com codigo, nome, cidade, sigla e administracao_direta
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._ug_cr:
            raise ValueError("Nenhuma 'unidade_gestora_cr' encontrada no blueprint.")

        return self._ug_cr

    def unidade_requisicao_cr(self) -> dict:
        """
        Retorna os dados da Unidade de Requisição de teste do módulo Corporativo
        (chave `unidade_requisicao_cr` do blueprint).

        :return: Dicionário com sigla_ua, nome, endereco e centro_custo
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._ur_cr:
            raise ValueError("Nenhuma 'unidade_requisicao_cr' encontrada no blueprint.")

        return self._ur_cr

    def unidade_localizacao_cr(self) -> dict:
        """
        Retorna os dados da Unidade de Localização de teste do módulo Corporativo
        (chave `unidade_localizacao_cr` do blueprint).

        :return: Dicionário com sigla, unidade_administrativa, endereco,
            centro_custo e responsavel{nome, funcao}
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._ul_cr:
            raise ValueError(
                "Nenhuma 'unidade_localizacao_cr' encontrada no blueprint."
            )

        return self._ul_cr

    def centro_custo_cr(self) -> dict:
        """
        Retorna os dados do Centro de Custos de teste do módulo Corporativo
        (chave `centro_custo_cr` do blueprint).

        :return: Dicionário com nome
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._cc_cr:
            raise ValueError("Nenhum 'centro_custo_cr' encontrado no blueprint.")

        return self._cc_cr

    def almoxarifado_cr(self) -> dict:
        """
        Retorna os dados do Almoxarifado de teste do módulo Corporativo
        (chave `almoxarifado_cr` do blueprint).

        :return: Dicionário com nome, sigla e unidade_gestora
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._almoxarifado_cr:
            raise ValueError("Nenhum 'almoxarifado_cr' encontrado no blueprint.")

        return self._almoxarifado_cr

    def fornecedor_cr(self) -> dict:
        """
        Retorna os dados do Fornecedor de teste do módulo Corporativo
        (chave `fornecedor_cr` do blueprint).

        :return: Dicionário com nome, tipo, porte, endereco, cnpj, cidade, bairro, fone
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._fornecedor_cr:
            raise ValueError("Nenhum 'fornecedor_cr' encontrado no blueprint.")

        return self._fornecedor_cr

    def orgao_externo_cr(self) -> dict:
        """
        Retorna os dados do Órgão Externo de teste do módulo Corporativo
        (chave `orgao_externo_cr` do blueprint).

        :return: Dicionário com nome, sigla, cnpj, uasg, endereco, bairro, cidade, cep, fone, email
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._orgao_externo_cr:
            raise ValueError("Nenhum 'orgao_externo_cr' encontrado no blueprint.")

        return self._orgao_externo_cr

    def orgao_externo(self) -> dict:
        """
        Retorna os dados do Órgão Externo
        (chave `orgao_externo` do blueprint).

        :return: Dicionário com nome, sigla, cnpj, endereco, bairro, cidade
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._orgao_externo:
            raise ValueError("Nenhum 'orgao_externo' encontrado no blueprint.")

        return self._orgao_externo

    def portador_cr(self) -> dict:
        """
        Retorna os dados do Portador de teste do módulo Corporativo
        (chave `portador_cr` do blueprint).

        :return: Dicionário com nome, cpf, rg, endereco, cidade, cep, fone, fornecedor, email
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._portador_cr:
            raise ValueError("Nenhum 'portador_cr' encontrado no blueprint.")

        return self._portador_cr

    def pais_cr(self) -> dict:
        """Dados do País de teste do Corporativo (chave `pais_cr`)."""
        if not self._pais_cr:
            raise ValueError("Nenhum 'pais_cr' encontrado no blueprint.")
        return self._pais_cr

    def regiao_cr(self) -> dict:
        """Dados da Região de teste do Corporativo (chave `regiao_cr`)."""
        if not self._regiao_cr:
            raise ValueError("Nenhuma 'regiao_cr' encontrada no blueprint.")
        return self._regiao_cr

    def uf_cr(self) -> dict:
        """Dados da UF de teste do Corporativo (chave `uf_cr`)."""
        if not self._uf_cr:
            raise ValueError("Nenhuma 'uf_cr' encontrada no blueprint.")
        return self._uf_cr

    def cidade_cr(self) -> dict:
        """Dados da Cidade de teste do Corporativo (chave `cidade_cr`)."""
        if not self._cidade_cr:
            raise ValueError("Nenhuma 'cidade_cr' encontrada no blueprint.")
        return self._cidade_cr

    def instalacao_cr(self) -> dict:
        """Dados da Instalação de teste do Corporativo (chave `instalacao_cr`)."""
        if not self._instalacao_cr:
            raise ValueError("Nenhuma 'instalacao_cr' encontrada no blueprint.")
        return self._instalacao_cr

    def endereco_cr(self) -> dict:
        """Dados do Endereço de teste do Corporativo (chave `endereco_cr`)."""
        if not self._endereco_cr:
            raise ValueError("Nenhum 'endereco_cr' encontrado no blueprint.")
        return self._endereco_cr

    def funcao_cr(self) -> dict:
        """Dados da Função de teste do Corporativo (chave `funcao_cr`)."""
        if not self._funcao_cr:
            raise ValueError("Nenhuma 'funcao_cr' encontrada no blueprint.")
        return self._funcao_cr

    def funcionario_cr(self) -> dict:
        """Dados do Funcionário de teste do Corporativo (chave `funcionario_cr`)."""
        if not self._funcionario_cr:
            raise ValueError("Nenhum 'funcionario_cr' encontrado no blueprint.")
        return self._funcionario_cr

    def unidade_medida_cr(self) -> dict:
        """Dados da Unidade de Medida de teste do Corporativo (chave `unidade_medida_cr`)."""
        if not self._unidade_medida_cr:
            raise ValueError("Nenhuma 'unidade_medida_cr' encontrada no blueprint.")
        return self._unidade_medida_cr

    def material_consumo_cr(self) -> dict:
        """Dados do Material de Consumo de teste do Corporativo (chave `material_consumo_cr`)."""
        if not self._material_consumo_cr:
            raise ValueError("Nenhum 'material_consumo_cr' encontrado no blueprint.")
        return self._material_consumo_cr

    def material_permanente_cr(self) -> dict:
        """Dados do Material Permanente de teste do Corporativo (chave `material_permanente_cr`)."""
        if not self._material_permanente_cr:
            raise ValueError("Nenhum 'material_permanente_cr' encontrado no blueprint.")
        return self._material_permanente_cr

    def material_servico_cr(self) -> dict:
        """Dados do Material Serviço de teste do Corporativo (chave `material_servico_cr`)."""
        if not self._material_servico_cr:
            raise ValueError("Nenhum 'material_servico_cr' encontrado no blueprint.")
        return self._material_servico_cr

    def modelo_importacao_cr(self) -> dict:
        """Dados do Modelo de Importação de teste do Corporativo (chave `modelo_importacao_cr`)."""
        if not self._modelo_importacao_cr:
            raise ValueError("Nenhum 'modelo_importacao_cr' encontrado no blueprint.")
        return self._modelo_importacao_cr

    def supply_cr(self) -> dict:
        """Dados do Supply de teste do Corporativo (chave `supply_cr`)."""
        if not self._supply_cr:
            raise ValueError("Nenhum 'supply_cr' encontrado no blueprint.")
        return self._supply_cr

    def caracteristica_bem_cr(self) -> dict:
        """Dados da Característica do Bem de teste do Corporativo (chave `caracteristica_bem_cr`)."""
        if not self._caracteristica_bem_cr:
            raise ValueError("Nenhum 'caracteristica_bem_cr' encontrado no blueprint.")
        return self._caracteristica_bem_cr

    def perfil_cr(self) -> dict:
        """Dados do Perfil de teste do Corporativo (chave `perfil_cr`)."""
        if not self._perfil_cr:
            raise ValueError("Nenhum 'perfil_cr' encontrado no blueprint.")
        return self._perfil_cr

    def funcionario_usuario_cr(self) -> dict:
        """Dados do Funcionário+Usuário de teste do Corporativo (chave `funcionario_usuario_cr`)."""
        if not self._funcionario_usuario_cr:
            raise ValueError("Nenhum 'funcionario_usuario_cr' encontrado no blueprint.")
        return self._funcionario_usuario_cr

    def ug(self) -> dict:
        """
        Retorna a Unidade Gestora do cliente ativo.

        Exige `codigo`, `nome` e `sigla` preenchidos no configs.yaml: os campos
        de U.G. da automação são preenchidos pelo código, então a ausência dele
        precisa falhar de forma explícita, e não preencher o campo em branco.

        :return: Dicionário de UG
        :rtype: dict
        :raises ValueError: Caso o cliente não tenha UG configurada ou a UG
            esteja sem código.
        """
        if not self._ug:
            raise ValueError("Nenhuma UG encontrada para este cliente.")

        if not str(self._ug.get("codigo") or "").strip():
            cliente = self._dados_cliente.get("cliente", "?")
            raise ValueError(
                f"UG do cliente '{cliente}' está sem 'codigo' no configs.yaml. "
                f"Preencha clientes.{cliente}.unidade_gestora.codigo — a automação "
                f"preenche os campos de U.G. pelo código, não pela sigla."
            )

        return self._ug

    def urs(self) -> list:
        """
        Retorna a lista de Unidades Requisitantes.

        :return: Lista de URs
        :rtype: list
        :raises ValueError: Se nenhuma UR for encontrada para o cliente.
        """
        if not self._urs:
            raise ValueError("Nenhuma UR encontrada para este cliente.")

        return self._urs

    def ur_por_indice(self, indice: int) -> dict:
        """
        Retorna uma Unidade Requisitante baseada no índice.

        :param indice: Índice da UR desejada
        :type indice: int
        :return: Dicionário da UR
        :rtype: dict
        :raises IndexError: Se o índice estiver fora do intervalo válido.
        """
        urs = self.urs()

        if indice < 0 or indice >= len(urs):
            raise IndexError(
                f"Índice inválido: {indice}. Intervalo válido: 0 a {len(urs) - 1}"
            )

        return urs[indice]

    def ur_qualquer(self) -> dict:
        """
        Retorna uma Unidade Requisitante aleatória.

        :return: Dicionário de uma UR aleatória
        :rtype: dict
        """
        return random.choice(self.urs())

    def ur_padrao(self) -> dict:
        """
        Retorna a Unidade Requisitante padrão (primeira da lista).

        :return: Dicionário da primeira UR
        :rtype: dict
        """
        return self.ur_por_indice(0)

    def almoxarifados(self) -> list:
        """
        Retorna os almoxarifados.

        :return: Lista de dicionários de almoxarifado
        :rtype: list
        """
        if not self._almoxarifados:
            raise ValueError("Nenhum almoxarifado encontrado para este cliente.")

        return self._almoxarifados

    def almoxarifado_qualquer(self) -> dict:
        """
        Retorna um almoxarifado aleatório dentre os almoxarifados disponíveis
        no contexto do cliente.

        :return: Dicionário contendo os dados de um almoxarifado aleatório
        :rtype: dict
        """
        return random.choice(self.almoxarifados())

    def almoxarifado_por_indice(self, indice: int) -> dict:
        """
        Retorna um almoxarifado com base no índice dentro da coleção de
        almoxarifados disponíveis no contexto do cliente.

        A ordem dos almoxarifados segue a ordem de inserção do dicionário
        original carregado nos dados brutos do cliente.

        :param indice: Índice do almoxarifado desejado (iniciando em 0)
        :type indice: int
        :return: Dados do almoxarifado correspondente ao índice informado
        :rtype: dict
        :raises IndexError: Caso o índice informado seja menor que zero ou
        maior que o último índice disponível
        """
        almoxarifados = self.almoxarifados()

        if indice < 0 or indice >= len(almoxarifados):
            raise IndexError(
                f"Índice inválido: {indice}. Intervalo válido: 0 a {len(almoxarifados) - 1}"
            )

        return almoxarifados[indice]

    def almoxarifado_padrao(self) -> dict:
        """
        Retorna o almoxarifado padrão do cliente.

        O almoxarifado padrão corresponde ao primeiro almoxarifado
        cadastrado na coleção de almoxarifados do contexto do cliente.

        :return: Dicionário contendo os dados do almoxarifado padrão
        :rtype: dict
        :raises IndexError: Caso não existam almoxarifados cadastrados
        """
        return self.almoxarifado_por_indice(0)

    def fornecedores(self) -> list:
        """
        Retorna todos os fornecedores do cliente.

        :raises ValueError: Caso não sejam encontrados fornecedores
        :return: Lista de dicionários de fornecedor
        :rtype: list
        """
        if not self._fornecedores:
            raise ValueError("Nenhum fornecedor encontrado para este cliente.")

        return self._fornecedores

    def fornecedor_qualquer(self) -> dict:
        """
        Retorna um fornecedor aleatório do cliente.

        A seleção é feita de forma uniforme entre os fornecedores disponíveis.

        :return: Dados de um fornecedor selecionado aleatoriamente
        :rtype: dict
        :raises ValueError: Caso não sejam encontrados fornecedores
        """
        return random.choice(self.fornecedores())

    def fornecedor_por_indice(self, indice: int) -> dict:
        """
        Retorna um fornecedor com base em sua posição (índice).

        A indexação segue a ordem definida nos dados de entrada.

        :param indice: Índice do fornecedor desejado (base 0)
        :type indice: int
        :return: Dados do fornecedor correspondente ao índice
        :rtype: dict
        :raises IndexError: Se o índice estiver fora do intervalo válido
        """
        fornecedores = self.fornecedores()

        if indice < 0 or indice >= len(fornecedores):
            raise IndexError(
                f"Índice inválido: {indice}. Intervalo válido: 0 a {len(fornecedores) - 1}"
            )

        return fornecedores[indice]

    def fornecedor_padrao(self) -> dict:
        """
        Retorna o fornecedor padrão do cliente.

        O fornecedor padrão é o primeiro fornecedor na lista de fornecedores
        do cliente.

        :return: Dados do fornecedor padrão do cliente
        :rtype: dict
        """
        return self.fornecedor_por_indice(0)

    def materiais(self) -> list:
        """
        Retorna a lista de materiais do cliente.

        :return: Lista de materiais
        :rtype: list
        :raises ValueError: Se nenhum material for encontrado para o cliente.
        """
        if not self._materiais:
            raise ValueError("Nenhum material encontrado para este cliente.")

        return self._materiais

    def materiais_por_quantidade(self, quantidade: int = 20) -> list:
        """
        Retorna a lista de materiais do cliente com a quantidade especificada.

        :param quantidade: Número de bens desejados (padrão: 20)
        :type quantidade: int
        :return: Lista com quantidade desejada de materiais
        :rtype: list
        :raises ValueError: Se a quantidade de materiais for <= 0 ou se o cliente tiver menos materiais que o desejado.
        """
        if quantidade <= 0:
            raise ValueError(
                f"A quantidade deve ser maior que 0. Recebido: {quantidade}"
            )

        materiais = self.materiais()

        if len(materiais) < quantidade:
            raise ValueError(
                f"Quantidade de bens encontrados ({len(materiais)}) menor que o solicitado ({quantidade}) para esse cliente."
            )

        return materiais[:quantidade]

    def material_qualquer(self) -> dict:
        """
        Retorna um material aleatório da lista.

        :return: Dicionário de um material aleatório
        :rtype: dict
        """
        materiais = self.materiais()
        return random.choice(materiais)

    def material_por_indice(self, indice: int) -> dict:
        """
        Retorna um material específico baseado no índice.

        :param indice: Índice do material desejado
        :type indice: int
        :return: Dicionário do material
        :rtype: dict
        :raises IndexError: Se o índice estiver fora do intervalo válido.
        """
        materiais = self.materiais()

        if indice < 0 or indice >= len(materiais):
            raise IndexError(
                f"Índice inválido: {indice}. Intervalo válido: 0 a {len(materiais) - 1}"
            )

        return materiais[indice]

    def material_padrao(self) -> dict:
        """
        Retorna o material padrão (primeiro da lista).

        :return: Dicionário do primeiro material
        :rtype: dict
        """
        return self.material_por_indice(0)

    def bens(self) -> list:
        """
        Retorna a lista de bens do cliente.

        :return: Lista de bens
        :rtype: list
        :raises ValueError: Se nenhum bem for encontrado para o cliente.
        """
        if not self._bens:
            raise ValueError("Nenhum bem encontrado para este cliente.")

        return self._bens

    def bens_por_quantidade(self, quantidade: int = 20) -> list:
        """
        Retorna a lista de bens do cliente com a quantidade especificada.

        :param quantidade: Número de bens desejados (padrão: 20)
        :type quantidade: int
        :return: Lista com quantidade desejada de bens
        :rtype: list
        :raises ValueError: Se a quantidade de bens for <= 0 ou se o cliente tiver menos bens que o desejado.
        """
        if quantidade <= 0:
            raise ValueError(
                f"A quantidade deve ser maior que 0. Recebido: {quantidade}"
            )

        bens = self.bens()

        if len(bens) < quantidade:
            raise ValueError(
                f"Quantidade de bens encontrados ({len(bens)}) menor que o solicitado ({quantidade}) para esse cliente."
            )

        return bens[:quantidade]

    def bem_por_indice(self, indice: int) -> dict:
        """
        Retorna um bem específico baseado no índice.

        :param indice: Índice do bem desejado
        :type indice: int
        :return: Dicionário do bem
        :rtype: dict
        :raises IndexError: Se o índice estiver fora do intervalo válido.
        """
        bens = self.bens()

        if indice < 0 or indice >= len(bens):
            raise IndexError(
                f"Índice inválido: {indice}. Intervalo válido: 0 a {len(bens) - 1}"
            )

        return bens[indice]

    def bem_padrao(self) -> dict:
        """
        Retorna o bem padrão (primeiro da lista).

        :return: Dicionário do primeiro bem
        :rtype: dict
        """
        return self.bem_por_indice(0)

    def enderecos_material(self) -> list:
        """
        Retorna a lista de endereços do material.

        :return: Lista de endereços
        :rtype: list
        """
        return self._enderecos_material

    def endereco_material_por_indice(self, indice: int) -> dict:
        """
        Retorna um endereço de material específico baseado no índice.

        :param indice: Índice do endereço desejado
        :type indice: int
        :return: Dicionário do endereço
        :rtype: dict
        :raises IndexError: Se o índice estiver fora do intervalo válido.
        """
        enderecos_material = self.enderecos_material()

        if indice < 0 or indice >= len(enderecos_material):
            raise IndexError(
                f"Índice inválido: {indice}. Intervalo válido: 0 a {len(enderecos_material) - 1}"
            )

        return enderecos_material[indice]

    def endereco_material_padrao(self) -> dict:
        """
        Retorna o endereço de material padrão (primeiro da lista).

        :return: Dicionário do primeiro endereço
        :rtype: dict
        """
        return self.endereco_material_por_indice(0)

    def unidades_localizacao(self) -> list:
        """
        Retorna a lista de unidades de localização.

        :return: Lista de unidades de localização
        :rtype: list
        """
        return self._unidades_localizacao

    def unidade_localizacao_por_indice(self, indice: int) -> dict:
        """
        Retorna uma unidade de localização específica baseada no índice.

        :param indice: Índice da unidade de localização desejada
        :type indice: int
        :return: Dicionário da unidade de localização
        :rtype: dict
        :raises IndexError: Se o índice estiver fora do intervalo válido.
        """
        unidades_localizacao = self.unidades_localizacao()

        if indice < 0 or indice >= len(unidades_localizacao):
            raise IndexError(
                f"Índice inválido: {indice}.Intervalo válido: 0 a {len(unidades_localizacao) - 1}"
            )

        return unidades_localizacao[indice]

    def unidade_localizacao_padrao(self) -> dict:
        """
        Retorna a unidade de localização padrão (primeira da lista).

        :return: Dicionário da primeira unidade de localização
        :rtype: dict
        """
        return self.unidade_localizacao_por_indice(0)

    def unidade_localizacao_estoque(self) -> dict:
        """
        Retorna a unidade de localização de estoque do cliente.

        A UL de estoque é dado de configuração do cliente (como a UG): vem do
        configs.yaml (clientes.<cliente>.unidade_localizacao_estoque) via
        conftest, não do blueprint.

        :return: Dicionário com codigo e sigla
        :rtype: dict
        :raises ValueError: Caso o cliente não tenha UL de estoque configurada.
        """
        if not self._unidade_localizacao_estoque:
            raise ValueError("Nenhuma UL de estoque encontrada para este cliente.")

        return self._unidade_localizacao_estoque

    def funcionarios(self) -> list:
        """
        Retorna a lista de funcionários.

        :return: Lista de funcionários
        :rtype: list
        """
        return self._funcionarios

    def funcionario_por_indice(self, indice: int) -> dict:
        """
        Retorna um funcionário específico baseado no índice.

        :param indice: Índice do funcionário desejado
        :type indice: int
        :return: Dicionário do funcionário
        :rtype: dict
        :raises IndexError: Se o índice estiver fora do intervalo válido.
        """
        funcionarios = self.funcionarios()

        if indice < 0 or indice >= len(funcionarios):
            raise IndexError(
                f"Índice inválido: {indice}. Intervalo válido: 0 a {len(funcionarios) - 1}"
            )

        return funcionarios[indice]

    def funcionario_padrao(self) -> dict:
        """
        Retorna o funcionário padrão (primeiro da lista).

        :return: Dicionário do primeiro funcionário
        :rtype: dict
        """
        return self.funcionario_por_indice(5)

    def evento(self) -> dict:
        """
        Retorna os dados do Evento
        (chave `evento` do blueprint).

        :return: Dicionário com nome
        :rtype: dict
        :raises ValueError: Caso a chave não exista no blueprint.
        """
        if not self._evento:
            raise ValueError("Nenhum 'evento' encontrado no blueprint.")

        return self._evento

    def grupos(self) -> list:
        """
        Retorna os almoxarifados.

        :return: Lista de dicionários de almoxarifado
        :rtype: list
        """
        if not self._grupos:
            raise ValueError("Nenhum almoxarifado encontrado para este cliente.")

        return self._grupos

    def centro_custo(self) -> dict:
        """Retorna o Centro de Custo persistente usado como massa-base do Genesis."""
        if not self._centro_custo:
            raise ValueError("Nenhum 'centro_custo' encontrado no blueprint.")
        return self._centro_custo

    def instalacao(self) -> dict:
        """Retorna a Instalação persistente usada como massa-base do Genesis."""
        if not self._instalacao:
            raise ValueError("Nenhuma 'instalacao' encontrada no blueprint.")
        return self._instalacao

    def enderecos(self) -> list:
        """Retorna os Endereços persistentes do blueprint; ausência resulta em lista vazia."""
        return self._enderecos

    def catalogo(self) -> dict:
        """Retorna a Instalação persistente usada como massa-base do Genesis."""
        if not self._catalogo:
            raise ValueError("Nenhuma 'instalacao' encontrada no blueprint.")
        return self._catalogo
