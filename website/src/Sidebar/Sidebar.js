import formatDistance from "date-fns/formatDistance";

const Sidebar = ({ model }) => {
  return model ? (
    <div className="ms-4">
      <div className="mb-4">
        <div className="fw-bold small">Created</div>
        <div className="small">
          {model.created &&
            formatDistance(
              new Date(model.created.replace(" ", "T") + "Z"),
              new Date(),
              { addSuffix: true }
            )}
        </div>
      </div>
      <div className="mb-4">
        <div className="fw-bold small">Archived</div>
        <div className="small">{model.archived ? "Yes" : "No"}</div>
      </div>
    </div>
  ) : null;
};

export default Sidebar;
