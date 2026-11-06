// Toda a comunicação com a API fica aqui. Os componentes só chamam estas funções.

const BASE = "/api"; // o proxy do Vite repassa para http://localhost:8000

// Transforma o erro devolvido pela API em uma mensagem que o usuário entenda.
function extrairMensagem(corpo, status) {
  const detalhe = corpo?.detail;
  if (typeof detalhe === "string") return detalhe;
  if (Array.isArray(detalhe)) {
    // Erros de validação (422) vêm como lista; mostramos campo + motivo.
    return detalhe
      .map((d) => `${d.loc?.[d.loc.length - 1] ?? "campo"}: ${d.msg}`)
      .join("; ");
  }
  return `A API respondeu com erro ${status}.`;
}

// Função base: faz a requisição, trata erros e devolve o JSON da resposta.
async function requisicao(caminho, opcoes = {}) {
  let resposta;
  try {
    resposta = await fetch(BASE + caminho, {
      headers: { "Content-Type": "application/json" },
      ...opcoes,
    });
  } catch {
    // fetch só falha assim quando não consegue falar com o servidor.
    throw new Error("Não foi possível falar com a API. Confira se ela está rodando.");
  }

  if (!resposta.ok) {
    let corpo = null;
    try {
      corpo = await resposta.json();
    } catch {
      // resposta sem JSON: usamos a mensagem genérica
    }
    throw new Error(extrairMensagem(corpo, resposta.status));
  }

  if (resposta.status === 204) return null; // 204 = sucesso sem conteúdo (ex.: exclusão)
  return resposta.json();
}

// Monta "?status=aberto&tipo=rede" só com os filtros preenchidos.
function montarQuery(filtros) {
  const parametros = new URLSearchParams();
  Object.entries(filtros).forEach(([chave, valor]) => {
    if (valor) parametros.set(chave, valor);
  });
  const texto = parametros.toString();
  return texto ? `?${texto}` : "";
}

export const api = {
  listar: (filtros) => requisicao(`/chamados${montarQuery(filtros)}`),
  resumo: () => requisicao("/chamados/resumo"),
  unidades: () => requisicao("/chamados/unidades"),
  criar: (dados) => requisicao("/chamados", { method: "POST", body: JSON.stringify(dados) }),
  atualizarStatus: (id, status) =>
    requisicao(`/chamados/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
  excluir: (id) => requisicao(`/chamados/${id}`, { method: "DELETE" }),
};
