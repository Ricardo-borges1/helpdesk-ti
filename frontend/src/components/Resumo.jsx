// Faixa de resumo no topo: uma barra com a proporção de cada status
// e, abaixo, a contagem de cada um. Clicar num status filtra a lista.
import { STATUS } from "../constants";

export default function Resumo({ resumo, statusAtivo, aoEscolherStatus }) {
  // Enquanto os dados não chegam, não desenhamos nada.
  if (!resumo) return <section className="resumo" aria-busy="true" />;

  const { total, por_status: porStatus, sla_estourados: estourados } = resumo;

  return (
    <section className="resumo" aria-label="Resumo dos chamados">
      {/* Barra segmentada: a largura de cada pedaço é a % daquele status no total. */}
      <div className="regua" role="img" aria-label={`${total} chamados no total`}>
        {total > 0 &&
          STATUS.map(({ valor }) => (
            <span
              key={valor}
              className={`regua-trecho status-${valor}`}
              style={{ width: `${(porStatus[valor] / total) * 100}%` }}
            />
          ))}
      </div>

      <div className="resumo-numeros">
        {STATUS.map(({ valor, rotulo }) => (
          <button
            key={valor}
            // aria-pressed informa a leitores de tela se o filtro está ligado.
            aria-pressed={statusAtivo === valor}
            className={`resumo-item status-${valor}${statusAtivo === valor ? " ativo" : ""}`}
            // Clicar de novo no status ativo desliga o filtro.
            onClick={() => aoEscolherStatus(statusAtivo === valor ? "" : valor)}
          >
            <span className="numero">{porStatus[valor]}</span>
            <span className="rotulo">{rotulo}</span>
          </button>
        ))}

        <div className="resumo-item sla">
          <span className="numero">{estourados}</span>
          <span className="rotulo">Com SLA estourado</span>
        </div>
      </div>

      {total === 0 && <p className="vazio">Nenhum chamado ainda. Abra o primeiro em "Novo chamado".</p>}
    </section>
  );
}
