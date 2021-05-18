import formatDistance from "date-fns/formatDistance";
import { Hexagon } from "react-feather";

import DataSet from "./DataSet";
import Path from "./Path";
import Pipeline from "./Pipeline";

const VersionCard = ({ model, version }) => (
  <div className="card mb-3">
    <div className="card-body">
      <div className="row py-1 flex-grow-1">
        <div className="col-4">
          <Hexagon color="#94A3B8" size={18} />
          <span className="px-1 small">
            {model.name} {version.tag.toLowerCase()}
          </span>
        </div>
        <div className="col-5 small text-muted">{version.hash}</div>
        <div className="col-3 small text-end text-muted">
          {formatDistance(
            new Date(version.created.replace(" ", "T") + "Z"),
            new Date(),
            { addSuffix: true }
          )
            .replace("about ", "")
            .replace("less than ", "")}
        </div>
      </div>
    </div>
    <div className="card-footer bg-white border-top-0 px-1 pt-0 pb-3 small text-muted">
      <ul className="list-inline mb-0">
        <li class="list-inline-item">
          <DataSet dataSet={version.dataSet} />
        </li>
        <li class="list-inline-item">
          <Pipeline pipeline={version.pipeline} />
        </li>
        <li class="list-inline-item">
          <Path path={version.path} />
        </li>
      </ul>
    </div>
  </div>
);

export default VersionCard;
