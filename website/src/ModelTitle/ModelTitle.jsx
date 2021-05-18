const ModelTitle = ({ model }) => {
  return model ? (
    <>
      <h3
        style={{
          fontFamily: "'Raleway', sans-serif",
          fontSize: "1.25em",
        }}
      >
        {model.name}
      </h3>
      <p className="text-muted">{model.description}</p>
    </>
  ) : null;
};

export default ModelTitle;
