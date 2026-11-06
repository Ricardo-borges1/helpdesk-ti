// Linha de filtros: busca por texto, tipo e unidade.
import { TIPOS } from "../constants";

export default function Filtros({ filtros, unidades, aoMudar, aoLimpar }) {
  // Só mostramos "Limpar filtros" quando existe algum filtro ligado.
  const temFiltro = Object.values(filtros).some(Boolean);

  return (
    <section className="filtros" aria-label="Filtros">
      <label className="campo campo-busca">
        <span>Buscar</span>
        <input
          type="search"
          placeholder="Título, descrição ou solicitante"
          value={filtros.busca}
          onChange={(e) => aoMudar({ busca: e.target.value })}
        />
      </label>

      <label className="campo">
        <span>Tipo</span>
        <select value={filtros.tipo} onChange={(e) => aoMudar({ tipo: e.target.value })}>
          <option value="">Todos</option>
          {TIPOS.map((t) => (
            <option key={t.valor} value={t.valor}>
              {t.rotulo}
            </option>
          ))}
        </select>
      </label>

      <label className="campo">
        <span>Unidade</span>
        <select value={filtros.unidade} onChange={(e) => aoMudar({ unidade: e.target.value })}>
          <option value="">Todas</option>
          {unidades.map((u) => (
            <option key={u} value={u}>
              {u}
            </option>
          ))}
        </select>
      </label>

      {temFiltro && (
        <button className="botao botao-texto" onClick={aoLimpar}>
          Limpar filtros
        </button>
      )}
    </section>
  );
}
