// src/App.jsx
import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/hello")
      .then((res) => res.json())
      .then((data) => setMessage(data.message));
  }, []);

  return (
    <div className="text-center p-10">
      <h1 className="text-3xl font-bold text-blue-500">Frontend React</h1>
      <p className="text-xl mt-4">Mensaje del backend: {message}</p>
    </div>
  );
}

export default App;
