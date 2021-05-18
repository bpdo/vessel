import { Database } from "react-feather";

const DataSet = ({ dataSet }) => {
  return dataSet ? (
    <div>
      <Database size={12} />
      <span className="px-1 small">{dataSet}</span>
    </div>
  ) : null;
};

export default DataSet;
