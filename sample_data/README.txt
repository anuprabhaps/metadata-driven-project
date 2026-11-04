Metadata-Driven Ingestion Sample Data

Included:
- sales.csv
- sales.xlsx
- sales.json
- sales.jsonl
- sales.tsv
- sales.xml
- metadata.yaml

Parquet:
Install pyarrow locally, then run:
  pip install pyarrow
  python -c "import pandas as pd; pd.read_csv('sample_data/sales.csv').to_parquet('sample_data/sales.parquet', index=False)"

To test another format, update source_config.file_format and file_pattern in metadata.yaml.
Supported examples: CSV/sales.csv, EXCEL/sales.xlsx, JSON/sales.json,
JSONL/sales.jsonl, TSV/sales.tsv, XML/sales.xml, PARQUET/sales.parquet.

The sample foreign key refers to dim_customer.cust_id, but no dimension file is included.
This is synthetic demonstration data, not real customer data.
