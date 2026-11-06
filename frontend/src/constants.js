// Listas usadas em vários lugares. "valor" é o que a API entende; "rotulo" é o que o usuário lê.
// Se mudar algo aqui, mude também em backend/app/schemas.py.

export const STATUS = [
  { valor: "aberto", rotulo: "Aberto" },
  { valor: "em_andamento", rotulo: "Em andamento" },
  { valor: "resolvido", rotulo: "Resolvido" },
  { valor: "fechado", rotulo: "Fechado" },
];

export const TIPOS = [
  { valor: "impressora", rotulo: "Impressora" },
  { valor: "rede", rotulo: "Rede" },
  { valor: "software", rotulo: "Software" },
  { valor: "hardware", rotulo: "Hardware" },
  { valor: "outros", rotulo: "Outros" },
];

// Busca o rótulo de um valor (ex.: "em_andamento" -> "Em andamento").
export function rotuloDe(lista, valor) {
  return lista.find((item) => item.valor === valor)?.rotulo ?? valor;
}
