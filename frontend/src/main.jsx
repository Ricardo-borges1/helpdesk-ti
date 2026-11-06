// Ponto de entrada do front-end: liga o componente App à div "root" do index.html.
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  // StrictMode ajuda a achar problemas durante o desenvolvimento (não afeta a versão final).
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
