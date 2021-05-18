import { useEffect, useState } from "react";

import Models from "./Models";
import ModelTitle from "./ModelTitle";
import Nav from "./Layout/Nav";
import Sidebar from "./Sidebar";
import TwoColumn from "./Layout/TwoColumn";
import VersionCard from "./VersionCard";

import "../node_modules/bootstrap/dist/css/bootstrap.css";

function App() {
  const [models, setModels] = useState([]);
  const [versions, setVersions] = useState([]);
  const [model, setModel] = useState(null);

  useEffect(() => {
    const fetch_models = async () => {
      const result = await fetch("/models/");
      const _models = await result.json();

      setModels(_models);
      // setModel(_models[0]);
    };

    fetch_models();
  }, []);

  useEffect(() => {
    const fetch_versions = async () => {
      if (!model) return;

      const result = await fetch(`/versions/?model_id=${model.id}`);
      const _versions = await result.json();
      setVersions(_versions);
    };

    fetch_versions();
  }, [model]);

  return (
    <>
      <Nav />
      <TwoColumn sidebar={<Models models={models} setModel={setModel} />}>
        <div className="row">
          <div className="col">
            <ModelTitle model={model} />
          </div>
        </div>
        <div className="row">
          <div className="col">
            {versions.map((v) => (
              <VersionCard model={model} version={v} />
            ))}
          </div>
          <div className="col-3">
            <Sidebar model={model} />
          </div>
        </div>
      </TwoColumn>
    </>
  );
}

export default App;
