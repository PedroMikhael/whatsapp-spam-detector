import { useState } from "react";

function App() {
  const [texto, setTexto] = useState("");
  const [resultado, setResultado] = useState("");

  const verificarSpam = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/api/spam/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto }),
      });
      const data = await response.json();
      setResultado(data.mensagem);
    } catch (err) {
      setResultado("Erro ao verificar a mensagem.");
      console.error(err);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Detector de Spam</h1>
      <input
        type="text"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        placeholder="Digite sua mensagem"
        style={{ width: "300px", marginRight: "1rem" }}
      />
      <button onClick={verificarSpam}>Verificar</button>
      <p>{resultado}</p>
    </div>
  );
}

export default App;










