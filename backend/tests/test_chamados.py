"""Testes automáticos da API. Rode com: pytest"""

CHAMADO_EXEMPLO = {
    "titulo": "Impressora não imprime",
    "descricao": "Aparece erro de spooler no setor de compras",
    "solicitante": "Maria",
    "unidade": "Secretaria de Administração",
    "tipo": "impressora",
}


def criar(client, **mudancas):
    """Atalho: cria um chamado de exemplo, trocando só os campos pedidos."""
    return client.post("/chamados", json={**CHAMADO_EXEMPLO, **mudancas})


def test_health(client):
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_criar_chamado(client):
    resposta = criar(client)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] == 1
    assert corpo["status"] == "aberto"
    assert corpo["resolvido_em"] is None
    assert corpo["sla_estourado"] is False
    assert corpo["prazo_sla"] is not None


def test_titulo_curto_demais_da_422(client):
    assert criar(client, titulo="ab").status_code == 422


def test_tipo_invalido_da_422(client):
    assert criar(client, tipo="geladeira").status_code == 422


def test_listar_e_filtrar(client):
    criar(client)
    criar(client, titulo="Sem internet", tipo="rede", unidade="UBS Central")

    assert len(client.get("/chamados").json()) == 2
    assert len(client.get("/chamados?tipo=rede").json()) == 1
    assert len(client.get("/chamados?unidade=UBS Central").json()) == 1
    assert len(client.get("/chamados?busca=internet").json()) == 1
    assert len(client.get("/chamados?status=fechado").json()) == 0


def test_obter_chamado_inexistente_da_404(client):
    assert client.get("/chamados/99").status_code == 404


def test_resolver_preenche_data_e_reabrir_limpa(client):
    criar(client)

    resolvido = client.patch("/chamados/1/status", json={"status": "resolvido"}).json()
    assert resolvido["status"] == "resolvido"
    assert resolvido["resolvido_em"] is not None

    reaberto = client.patch("/chamados/1/status", json={"status": "aberto"}).json()
    assert reaberto["resolvido_em"] is None


def test_status_invalido_da_422(client):
    criar(client)
    assert client.patch("/chamados/1/status", json={"status": "pendente"}).status_code == 422


def test_excluir_chamado(client):
    criar(client)
    assert client.delete("/chamados/1").status_code == 204
    assert client.get("/chamados/1").status_code == 404
    assert client.delete("/chamados/1").status_code == 404


def test_resumo(client):
    criar(client)
    criar(client)
    client.patch("/chamados/2/status", json={"status": "resolvido"})

    resumo = client.get("/chamados/resumo").json()
    assert resumo["total"] == 2
    assert resumo["por_status"]["aberto"] == 1
    assert resumo["por_status"]["resolvido"] == 1
    assert resumo["sla_estourados"] == 0


def test_unidades(client):
    criar(client, unidade="UBS Central")
    criar(client, unidade="Almoxarifado Central")
    criar(client, unidade="UBS Central")
    assert client.get("/chamados/unidades").json() == ["Almoxarifado Central", "UBS Central"]
