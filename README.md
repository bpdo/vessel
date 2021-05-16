# vessel

a machine learning model registry

### Getting Started

```
make
```

### Environment Variables

| Name              | Description                             | Default Value       |
| ----------------- | --------------------------------------- | ------------------- |
| CHUNK_SIZE        | Buffer size for reading files, in bytes | 8192                |
| CONNECTION_STRING | Database connection string              | sqlite:///vessel.db |
| FILE_PATH         | Path where model files will be written  | /tmp/vessel         |
