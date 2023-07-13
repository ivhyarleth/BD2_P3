import React, { useState, useRef } from "react";
import axios from "axios";
import Camera from "/camera.jpg";

const Buscador = () => {
  const [k, setK] = useState("");
  const [src, setSrc] = useState("");
  const [files, setFiles] = useState([]);
  const [response, setResponse] = useState([]);
  const [page, setPage] = useState(1);
  const [length, setLength] = useState(1);
  const [total, setTotal] = useState(7);
  const [search, setSearch] = useState(null);
  const [radius, setRadius] = useState(null);

  const inputFileRef = useRef(null);
  const photoPlaceholder = Camera;

  const options = [
    { value: null, text: "Select an option" },
    { value: "sequential", text: "KNN-Sequential" },
    { value: "priority", text: "KNN-RTree" },
    { value: "range", text: "KNN-RTree By Range" },
    { value: "highd", text: "KNN-HighD" },
  ];

  const submitFile = () => {
    const formData = new FormData();
    formData.append("file", files);
    const data = {
      k: k === "" ? 1 : Number(k),
      search: search === "" ? "priority" : search,
    };
    if (radius !== null) {
      data.radius = Number(radius);
    }
    formData.append("data", JSON.stringify(data));
    axios
      .post("http://127.0.0.1:8082/query", formData, {
        headers: {
          "Content-Type": false,
          processData: false,
        },
      })
      .then((res) => {
        console.log("Respuesta local");
        console.log(res);
        setResponse(res.data);
        for (let i = 0; i < res.data.length; i++) {
          res.data[i][2] = "http://127.0.0.1:8082/" + res.data[i][2];
        }
        setLength(Math.ceil(res.data.length / 6));
      })
      .catch((e) => {
        console.log(e);
      });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFiles(e.target.files[0]);
    const reader = new FileReader();
    reader.onload = (e) => {
      setSrc(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const chunk = (arr, size) => {
    return Array.from({ length: Math.ceil(arr.length / size) }, (v, i) =>
      arr.slice(i * size, i * size + size)
    );
  };

  const calculateIndex = (person) => {
    return response.map((iter) => iter[2]).indexOf(person[2]) + 1;
  };

  const responseSplit = response.slice(6 * (page - 1), 6 * page);
  const chunkPersons = chunk(responseSplit, 3);

  return (
    <div className="container fs-3">
      <div className="row">
        <div className="mx-auto m-2" style={{ width: "400px" }}>
          <div className="image-upload">
            <label htmlFor="photo" className="cat-photo">
              <img
                className="cat-photo"
                src={src === "" ? photoPlaceholder : src}
                alt="Uploaded"
                width="500"
              />
            </label>
            <input
              id="photo"
              ref={inputFileRef}
              accept="image/*"
              type="file"
              onChange={handleFileChange}
            />
          </div>
          <div className="p-1">
            <div className="px-4 py-2">
              <div className="my-1">
                <div className="p-0">Type of Search:</div>
                <div className="p-0">
                  <select
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  >
                    {options.map((option) => (
                      <option value={option.value} key={option.value}>
                        {option.text}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              {search !== "range" && (
                <div className="my-1">
                  <div className="p-0">K results:</div>
                  <div className="p-0">
                    <input
                      min="1"
                      type="number"
                      value={k}
                      onChange={(e) => setK(e.target.value)}
                      placeholder="Number of k results"
                    />
                  </div>
                </div>
              )}
              {search === "range" && (
                <div className="my-1">
                  <div className="p-0">Radius:</div>
                  <div className="p-0">
                    <input
                      type="text"
                      pattern="[0-9]+([\.,][0-9]+)?"
                      value={radius}
                      onChange={(e) => setRadius(e.target.value)}
                      placeholder="Query radius"
                    />
                  </div>
                </div>
              )}
              <div className="mt-4">
                <button className="btn btn-primary btn-lg" onClick={submitFile}>
                  Submit
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <br />
      <div className="row justify-content-around">
        {response.length > 0 && <div>Results:</div>}
        <div className="text-center">
          <div>
            {response.length > 0 &&
              response.map((person, index) => (
                <div className="my-3" key={index}>
                  <div className="cat-photo">
                    <img src={person[2]} alt="Person" />
                  </div>
                  <div className="p-1">
                    <div className="p-3">
                      <div className="my-1">
                        <div className="p-0">Position:</div>
                        <div className="p-0">
                          <input value={calculateIndex(person)} readOnly />
                        </div>
                      </div>
                      <div className="my-1">
                        <div className="p-0">Name:</div>
                        <div className="p-0">
                          <input value={person[0]} />
                        </div>
                      </div>
                      <div className="my-1">
                        <div className="p-0">Distance:</div>
                        <div className="p-0">
                          <input value={person[1]} />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Buscador;
