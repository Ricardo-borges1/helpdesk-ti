// Configuração do Vite (a ferramenta que roda e empacota o front-end).
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Proxy: tudo que o front pedir em "/api/..." é repassado para a API em localhost:8000.
    // O "rewrite" tira o "/api" do caminho (/api/chamados vira /chamados).
    // Assim o navegador conversa só com uma origem e não há problema de CORS no desenvolvimento.
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (caminho) => caminho.replace(/^\/api/, ""),
      },
    },
  },
});
