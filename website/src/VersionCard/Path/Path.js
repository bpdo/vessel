import { Folder } from "react-feather";

const Path = ({ path }) => {
  return path ? (
    <div>
      <Folder size={12} />
      <span className="px-1 small">{path}</span>
    </div>
  ) : null;
};

export default Path;
