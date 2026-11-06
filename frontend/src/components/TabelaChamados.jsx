// Tabela com a lista de chamados. Cada linha permite mudar o status ou excluir.
import { STATUS, TIPOS, rotuloDe } from "../constants";
import { descreverSla, formatarData } from "../utils";

export default function TabelaChamados({ chamados, carregando, aoMudarStatus, aoExcluir }) {
  if (!carregando && chamados.length === 0) {
    return (
      <p className="vazio">
        Nenhum chamado encontrado. Limpe os filtros ou abra um novo chamado.
      </p>
    );
  }

  return (
    // O wrapper permite rolar a tabela de lado em telas pequenas.
    <div className="tabela-area" aria-busy={carregando}>
      <table className="tabela">
        <thead>
          <tr>
            <th>Nº</th>
            <th>Chamado</th>
            <th>Tipo</th>
            <th>Aberto em</th>
            <th>SLA</th>
            <th>Status</th>
            <th>
              <span className="so-leitor">Ações</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {chamados.map((c) => {
            const sla = descreverSla(c);
            return (
              <tr key={c.id}>
                <td className="num">{c.id}</td>
                <td>
                  <strong className="titulo-chamado">{c.titulo}</strong>
                  <span className="detalhe">
                    {c.solicitante}, {c.unidade}
                  </span>
                </td>
                <td>{rotuloDe(TIPOS, c.tipo)}</td>
                <td className="num">{formatarData(c.aberto_em)}</td>
                <td>
                  <span className={`sla sla-${sla.nivel}`}>{sla.texto}</span>
                </td>
                <td>
                  {/* O próprio select é o botão de mudar status: escolher já salva. */}
                  <select
                    className={`seletor-status status-${c.status}`}
                    aria-label={`Status do chamado ${c.id}`}
                    value={c.status}
                    onChange={(e) => aoMudarStatus(c.id, e.target.value)}
                  >
                    {STATUS.map((s) => (
                      <option key={s.valor} value={s.valor}>
                        {s.rotulo}
                      </option>
                    ))}
                  </select>
                </td>
                <td>
                  <button
                    className="botao botao-texto botao-perigo"
                    aria-label={`Excluir chamado ${c.id}`}
                    onClick={() => aoExcluir(c)}
                  >
                    Excluir
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
