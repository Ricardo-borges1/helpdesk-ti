// Painel lateral para abrir um novo chamado.
import { useEffect, useState } from "react";
import { TIPOS } from "../constants";

const FORM_VAZIO = { titulo: "", descricao: "", solicitante: "", unidade: "", tipo: "impressora" };

export default function FormChamado({ unidades, aoSalvar, aoFechar }) {
  const [dados, setDados] = useState(FORM_VAZIO);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  // Fecha o painel ao apertar Esc.
  useEffect(() => {
    const aoApertar = (evento) => evento.key === "Escape" && aoFechar();
    window.addEventListener("keydown", aoApertar);
    return () => window.removeEventListener("keydown", aoApertar);
  }, [aoFechar]);

  // Atualiza um campo: onChange={mudar("titulo")} troca só o "titulo".
  const mudar = (campo) => (evento) => setDados((atual) => ({ ...atual, [campo]: evento.target.value }));

  async function enviar(evento) {
    evento.preventDefault(); // impede o navegador de recarregar a página
    setErro("");
    setSalvando(true);
    try {
      await aoSalvar(dados);
    } catch (e) {
      setErro(e.message); // mostra o motivo que a API deu
      setSalvando(false);
    }
  }

  return (
    <div className="painel-fundo" onClick={aoFechar}>
      {/* stopPropagation: clicar dentro do painel não deve fechá-lo */}
      <aside
        className="painel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-painel"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="titulo-painel">Novo chamado</h2>

        <form onSubmit={enviar}>
          <label className="campo">
            <span>Título</span>
            <input
              autoFocus
              required
              minLength={3}
              maxLength={120}
              value={dados.titulo}
              onChange={mudar("titulo")}
              placeholder="Ex.: Impressora não imprime"
            />
          </label>

          <label className="campo">
            <span>Descrição</span>
            <textarea
              required
              minLength={3}
              rows={4}
              value={dados.descricao}
              onChange={mudar("descricao")}
              placeholder="O que acontece, desde quando e o que já foi tentado"
            />
          </label>

          <label className="campo">
            <span>Solicitante</span>
            <input required minLength={2} maxLength={100} value={dados.solicitante} onChange={mudar("solicitante")} />
          </label>

          <label className="campo">
            <span>Unidade</span>
            {/* datalist: o campo aceita qualquer texto, mas sugere as unidades já usadas */}
            <input required minLength={2} maxLength={100} list="lista-unidades" value={dados.unidade} onChange={mudar("unidade")} />
            <datalist id="lista-unidades">
              {unidades.map((u) => (
                <option key={u} value={u} />
              ))}
            </datalist>
          </label>

          <label className="campo">
            <span>Tipo</span>
            <select value={dados.tipo} onChange={mudar("tipo")}>
              {TIPOS.map((t) => (
                <option key={t.valor} value={t.valor}>
                  {t.rotulo}
                </option>
              ))}
            </select>
          </label>

          {erro && (
            <p className="mensagem-erro" role="alert">
              {erro}
            </p>
          )}

          <div className="painel-acoes">
            <button type="button" className="botao botao-texto" onClick={aoFechar}>
              Cancelar
            </button>
            <button type="submit" className="botao botao-primario" disabled={salvando}>
              {salvando ? "Salvando..." : "Abrir chamado"}
            </button>
          </div>
        </form>
      </aside>
    </div>
  );
}
