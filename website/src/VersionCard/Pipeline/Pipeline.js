import { GitCommit } from "react-feather";

const DataSet = ({ pipeline }) => {
  return pipeline ? (
    <div>
      <GitCommit size={12} />
      <span className="px-1 small">{pipeline}</span>
    </div>
  ) : null;
};

export default DataSet;
