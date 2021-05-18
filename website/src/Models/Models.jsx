import { useState } from "react";
import { Copy } from "react-feather";

const Models = ({ models, setModel }) => {
  const [search, setSearch] = useState("");

  return (
    <>
      <div className="fw-bold my-3 small">Models</div>
      <div className="mb-4">
        <input
          type="text"
          className="form-control form-control-sm"
          placeholder="Find a model..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <ul className="list-unstyled">
        {models
          .filter((m) => m.name.toLowerCase().includes(search.toLowerCase()))
          .map((m) => (
            <li className="list-group-unstyled d-flex mb-3 mx-1" key={m.name}>
              <Copy
                color={"#94A3B8"}
                size={16}
                className="mt-2 flex-shrink-0"
              />
              <div>
                <button
                  className="btn btn-sm btn-link py-0"
                  href={`/models/${m.id}`}
                  onClick={() => setModel(m)}
                >
                  {m.name.toLowerCase()}
                </button>
                <div className="ps-2 small text-muted">{m.description}</div>
              </div>
            </li>
          ))}
      </ul>
    </>
  );
};

export default Models;
