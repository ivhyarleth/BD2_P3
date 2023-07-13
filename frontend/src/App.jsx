import Buscador from "./components/Buscador"
import React from "react";

function App() {
  return (
      <div className="d-flex flex-column align-items-center justify-content-center mt-5">
        <h1
          style={{
            color: "#2d2d2d",
            fontFamily: "'Teko', sans-serif",
            fontSize: "4rem"
          }}
          >
          Proyecto 3
        </h1>
        <br />
        <div className="container">
          <Buscador />
        </div>
      </div>
  );
}

export default App;
