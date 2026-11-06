// Funções de apoio para mostrar datas e prazos de forma legível.

// Transforma uma data da API (texto ISO) em "29/10/2026 09:15", no horário do usuário.
export function formatarData(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}

// Transforma milissegundos em um texto curto: "2 d 3 h", "5 h 20 min" ou "40 min".
export function formatarDuracao(ms) {
  const minutosTotais = Math.max(0, Math.round(ms / 60000));
  const dias = Math.floor(minutosTotais / 1440);
  const horas = Math.floor((minutosTotais % 1440) / 60);
  const minutos = minutosTotais % 60;

  if (dias > 0) return `${dias} d ${horas} h`;
  if (horas > 0) return `${horas} h ${minutos} min`;
  return `${minutos} min`;
}

// Descreve a situação do SLA de um chamado.
// Devolve { texto, nivel }, onde "nivel" decide a cor: "ok", "atencao" ou "estourado".
export function descreverSla(chamado, agora = Date.now()) {
  // Chamado já resolvido: a API já diz se passou do prazo.
  if (chamado.resolvido_em) {
    return chamado.sla_estourado
      ? { texto: "Resolvido fora do prazo", nivel: "estourado" }
      : { texto: "Resolvido no prazo", nivel: "ok" };
  }

  // Chamado em aberto: compara o prazo com o momento atual.
  const diferenca = new Date(chamado.prazo_sla).getTime() - agora;
  if (diferenca < 0) {
    return { texto: `Estourou há ${formatarDuracao(-diferenca)}`, nivel: "estourado" };
  }
  const DUAS_HORAS = 2 * 60 * 60 * 1000;
  return {
    texto: `Vence em ${formatarDuracao(diferenca)}`,
    nivel: diferenca < DUAS_HORAS ? "atencao" : "ok",
  };
}
