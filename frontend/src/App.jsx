// Componente principal: guarda o estado da tela e conversa com a API.
import { useEffect, useState } from "react";
import { api } from "./api";
import Resumo from "./components/Resumo.jsx";
import Filtros from "./components/Filtros.jsx";
import TabelaChamados from "./components/TabelaChamados.jsx";
import FormChamado from "./components/FormChamado.jsx";

const FILTROS_VAZIOS = { status: "", tipo: "", unidade: "", busca: "" };

export default function App() {
  // useState guarda valores que, ao mudarem, fazem a tela se redesenhar.
  const [chamados, setChamados] = useState([]);
  const [resumo, setResumo] = useState(null);
  const [unidades, setUnidades] = useState([]);
  const [filtros, setFiltros] = useState(FILTROS_VAZIOS);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [painelAberto, setPainelAberto] = useState(false);
  const [aviso, setAviso] = useState("");
  // Número que sobe 1 a cada vez que queremos recarregar os dados (ex.: depois de salvar).
  const [versao, setVersao] = useState(0);

  const recarregar = () => setVersao((v) => v + 1);

  // useEffect roda quando a tela abre e sempre que "filtros" ou "versao" mudam.
  useEffect(() => {
    let cancelado = false; // evita que uma resposta antiga sobrescreva uma mais nova
    setCarregando(true);

    // Pequena espera (250 ms) para não chamar a API a cada letra digitada na busca.
    const espera = setTimeout(async () => {
      try {
        const [lista, numeros, listaUnidades] = await Promise.all([
          api.listar(filtros),
          api.resumo(),
          api.unidades(),
        ]);
        if (cancelado) return;
        setChamados(lista);
        setResumo(numeros);
        setUnidades(listaUnidades);
        setErro("");
      } catch (e) {
        if (!cancelado) setErro(e.message);
      } finally {
        if (!cancelado) setCarregando(false);
      }
    }, 250);

    // Função de limpeza: roda antes de um novo efeito, cancelando o anterior.
    return () => {
      cancelado = true;
      clearTimeout(espera);
    };
  }, [filtros, versao]);

  // O aviso ("Chamado aberto") some sozinho depois de 4 segundos.
  useEffect(() => {
    if (!aviso) return;
    const temporizador = setTimeout(() => setAviso(""), 4000);
    return () => clearTimeout(temporizador);
  }, [aviso]);

  // Atualiza só os filtros informados, mantendo os demais.
  const mudarFiltros = (parcial) => setFiltros((atual) => ({ ...atual, ...parcial }));

  async function criarChamado(dados) {
    // Se a API recusar, o erro sobe para o formulário, que mostra a mensagem.
    const novo = await api.criar(dados);
    setPainelAberto(false);
    setAviso(`Chamado #${novo.id} aberto.`);
    recarregar();
  }

  async function mudarStatus(id, status) {
    try {
      await api.atualizarStatus(id, status);
      setAviso(`Chamado #${id} atualizado.`);
      recarregar();
    } catch (e) {
      setErro(e.message);
    }
  }

  async function excluirChamado(chamado) {
    // confirm() abre a janelinha nativa de confirmação do navegador.
    if (!window.confirm(`Excluir o chamado #${chamado.id} "${chamado.titulo}"? Não dá para desfazer.`)) {
      return;
    }
    try {
      await api.excluir(chamado.id);
      setAviso(`Chamado #${chamado.id} excluído.`);
      recarregar();
    } catch (e) {
      setErro(e.message);
    }
  }

  return (
    <div className="pagina">
      <header className="topo">
        <h1>Chamados de TI</h1>
        <button className="botao botao-primario" onClick={() => setPainelAberto(true)}>
          Novo chamado
        </button>
      </header>

      {erro && (
        <p className="mensagem-erro" role="alert">
          {erro}
        </p>
      )}

      <Resumo
        resumo={resumo}
        statusAtivo={filtros.status}
        aoEscolherStatus={(status) => mudarFiltros({ status })}
      />

      <Filtros
        filtros={filtros}
        unidades={unidades}
        aoMudar={mudarFiltros}
        aoLimpar={() => setFiltros(FILTROS_VAZIOS)}
      />

      <TabelaChamados
        chamados={chamados}
        carregando={carregando}
        aoMudarStatus={mudarStatus}
        aoExcluir={excluirChamado}
      />

      {painelAberto && (
        <FormChamado
          unidades={unidades}
          aoSalvar={criarChamado}
          aoFechar={() => setPainelAberto(false)}
        />
      )}

      {/* role="status" faz leitores de tela anunciarem o aviso */}
      {aviso && (
        <p className="aviso" role="status">
          {aviso}
        </p>
      )}
    </div>
  );
}
