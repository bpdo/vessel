const TwoColumn = ({ children, sidebar }) => (
  <div className="row vh-100">
    <div className="col-3 border-end px-5">
      <div className="py-3 sticky-top">{sidebar}</div>
    </div>
    <div className="col py-4 px-5 bg-light">{children}</div>
  </div>
);

export default TwoColumn;
