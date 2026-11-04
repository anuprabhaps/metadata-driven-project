# from pathlib import Path

# import pandas as pd
# import yaml


# # Supported file formats and their corresponding readers
# SUPPORTED_FORMATS = {
#     "CSV": "csv",
#     "EXCEL": "excel",
#     "XLSX": "excel",
#     "XLS": "excel",
#     "PARQUET": "parquet",
#     "PQ": "parquet",
#     "JSON": "json",
#     "JSONL": "jsonl",
#     "NDJSON": "jsonl",
#     "TSV": "tsv",
#     "TXT": "txt",
#     "XML": "xml",
# }


# def load_metadata(metadata_path):
#     """Load and validate the basic structure of the YAML metadata."""

#     metadata_path = Path(metadata_path)

#     if not metadata_path.is_file():
#         raise FileNotFoundError(
#             f"Metadata file not found: {metadata_path}"
#         )

#     with metadata_path.open("r", encoding="utf-8") as file:
#         metadata = yaml.safe_load(file)

#     if not isinstance(metadata, dict):
#         raise ValueError("Metadata must contain a YAML mapping.")

#     source_config = metadata.get("source_config")

#     if not isinstance(source_config, dict):
#         raise ValueError("Missing or invalid source_config section.")

#     if not source_config.get("file_pattern"):
#         raise ValueError("Missing source_config.file_pattern.")

#     if not source_config.get("file_format"):
#         raise ValueError("Missing source_config.file_format.")

#     return metadata


# def read_data(file_path, source_config):
#     """Read a file dynamically based on its configured format."""

#     file_path = Path(file_path)

#     if not file_path.is_file():
#         raise FileNotFoundError(f"Source file not found: {file_path}")

#     file_format = str(
#         source_config["file_format"]
#     ).strip().upper()

#     reader_type = SUPPORTED_FORMATS.get(file_format)

#     if reader_type is None:
#         raise ValueError(
#             f"Unsupported file format: {file_format}"
#         )

#     encoding = source_config.get("encoding", "UTF-8")
#     header = 0 if source_config.get("header", True) else None

#     if reader_type == "csv":
#         data = pd.read_csv(
#             file_path,
#             sep=source_config.get("delimiter", ","),
#             header=header,
#             encoding=encoding,
#         )

#     elif reader_type == "tsv":
#         data = pd.read_csv(
#             file_path,
#             sep="\t",
#             header=header,
#             encoding=encoding,
#         )

#     elif reader_type == "txt":
#         data = pd.read_csv(
#             file_path,
#             sep=source_config.get("delimiter", None),
#             engine="python",
#             header=header,
#             encoding=encoding,
#         )

#     elif reader_type == "excel":
#         data = pd.read_excel(
#             file_path,
#             sheet_name=source_config.get("sheet_name", 0),
#             header=header,
#         )

#     elif reader_type == "parquet":
#         data = pd.read_parquet(file_path)

#     elif reader_type == "json":
#         data = pd.read_json(
#             file_path,
#             encoding=encoding,
#         )

#     elif reader_type == "jsonl":
#         data = pd.read_json(
#             file_path,
#             lines=True,
#             encoding=encoding,
#         )

#     elif reader_type == "xml":
#         data = pd.read_xml(file_path, encoding=encoding)

#     else:
#         raise ValueError(f"No reader implemented for {reader_type}")

#     if data.empty:
#         print(f"File successfully read, but contains zero records: {file_path}")
#     else:
#      print(f"File successfully ingested: {file_path}")



#     print(f"File successfully ingested: {file_path.name}")
#     print(f"Detected format: {file_format}")
#     print(f"Rows: {len(data)}")
#     print(f"Columns: {len(data.columns)}")

#     return data


# def ingest_delivery(delivery_directory, metadata_path=None):
#     """
#     Load metadata and ingest the configured source file.

#     delivery_directory:
#         Directory containing the client's source file.

#     metadata_path:
#         Path to metadata.yaml. Defaults to metadata.yaml
#         inside the delivery directory.
#     """

#     delivery_directory = Path(delivery_directory)

#     if metadata_path is None:
#         metadata_path = delivery_directory / "metadata.yaml"

#     metadata = load_metadata(metadata_path)
#     source_config = metadata["source_config"]

#     file_name = source_config["file_pattern"]
#     source_file = delivery_directory / file_name

#     # Prevent a configured filename from escaping the delivery folder.
#     if source_file.resolve().parent != delivery_directory.resolve():
#         raise ValueError(
#             "file_pattern must refer to a file directly "
#             "inside the delivery directory."
#         )

#     data = read_data(source_file, source_config)

#     return data, metadata


# if __name__ == "__main__":

#     delivery_folder = Path("sample_data")

#     try:
#         dataframe, metadata = ingest_delivery(delivery_folder)

#         print("\nIngestion completed successfully.")
#         print("\nPreview:")
#         print(dataframe.head())

#         print("\nColumn information:")
#         print(dataframe.dtypes)

#     except (FileNotFoundError, ValueError, OSError) as error:
#         print(f"Ingestion failed: {error}")



from pathlib import Path, PureWindowsPath

import pandas as pd
import yaml


# Supported formats and their Pandas readers.
# This is the framework's reader registry, not a list of client files.
SUPPORTED_FORMATS = {
    "CSV": "csv",
    "EXCEL": "excel",
    "XLSX": "excel",
    "XLS": "excel",
    "PARQUET": "parquet",
    "PQ": "parquet",
    "JSON": "json",
    "JSONL": "jsonl",
    "NDJSON": "jsonl",
    "TSV": "tsv",
    "TXT": "txt",
    "XML": "xml",
}

# Format is inferred from the extension when file_format is omitted.
EXTENSION_FORMATS = {
    ".csv": "CSV",
    ".xlsx": "EXCEL",
    ".xls": "EXCEL",
    ".parquet": "PARQUET",
    ".pq": "PARQUET",
    ".json": "JSON",
    ".jsonl": "JSONL",
    ".ndjson": "NDJSON",
    ".tsv": "TSV",
    ".txt": "TXT",
    ".xml": "XML",
}


def _validate_filename_pattern(pattern, source_id):
    """Allow a filename or wildcard pattern, but no directory traversal."""
    if not isinstance(pattern, str) or not pattern.strip():
        raise ValueError(
            f"Source '{source_id}' is missing source_config.file_pattern."
        )

    # Patterns must refer to files directly inside the delivery directory.
    if (
        Path(pattern).name != pattern
        or PureWindowsPath(pattern).name != pattern
        or Path(pattern).is_absolute()
        or PureWindowsPath(pattern).is_absolute()
        or ".." in pattern
    ):
        raise ValueError(
            f"Source '{source_id}': file_pattern must be a filename pattern "
            "inside the delivery directory; folder paths are not allowed."
        )


def load_metadata(metadata_path):
    """Load and validate delivery-level metadata and its source list."""
    metadata_path = Path(metadata_path)

    if not metadata_path.is_file():
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    try:
        with metadata_path.open("r", encoding="utf-8") as file:
            metadata = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML metadata file: {error}") from error

    if not isinstance(metadata, dict):
        raise ValueError("Metadata must contain a YAML mapping.")

    if not isinstance(metadata.get("delivery_metadata"), dict):
        raise ValueError("Missing or invalid delivery_metadata section.")

    sources = metadata.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Metadata must contain a non-empty 'sources' list.")

    source_ids = set()
    patterns = set()

    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise ValueError(f"Source entry {index} must be a YAML mapping.")

        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError(f"Source entry {index} needs a valid source_id.")
        if source_id in source_ids:
            raise ValueError(f"Duplicate source_id: {source_id}")
        source_ids.add(source_id)

        source_config = source.get("source_config")
        if not isinstance(source_config, dict):
            raise ValueError(
                f"Source '{source_id}' has a missing or invalid source_config."
            )

        pattern = source_config.get("file_pattern")
        _validate_filename_pattern(pattern, source_id)
        if pattern in patterns:
            raise ValueError(f"Duplicate file_pattern: {pattern}")
        patterns.add(pattern)

        # file_format is optional. If present, validate it; otherwise it is
        # inferred separately for every matched file from its extension.
        configured_format = source_config.get("file_format")
        if configured_format:
            normalized = str(configured_format).strip().upper()
            if normalized not in SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported file_format '{configured_format}' "
                    f"for source '{source_id}'."
                )

    return metadata


def _get_file_format(file_path, source_config):
    configured_format = source_config.get("file_format")
    if configured_format:
        return str(configured_format).strip().upper()
    return EXTENSION_FORMATS.get(Path(file_path).suffix.lower())


def read_data(file_path, source_config):
    """Read one file. Its format is configured or inferred from extension."""
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    file_format = _get_file_format(file_path, source_config)
    reader_type = SUPPORTED_FORMATS.get(file_format)
    if reader_type is None:
        raise ValueError(
            f"Cannot determine a supported format for '{file_path.name}'. "
            "Provide a supported file extension or set file_format in metadata."
        )

    encoding = source_config.get("encoding", "UTF-8")
    header = 0 if source_config.get("header", True) else None

    if reader_type == "csv":
        data = pd.read_csv(
            file_path,
            sep=source_config.get("delimiter", ","),
            header=header,
            encoding=encoding,
        )
    elif reader_type == "tsv":
        data = pd.read_csv(
            file_path, sep="\t", header=header, encoding=encoding
        )
    elif reader_type == "txt":
        data = pd.read_csv(
            file_path,
            sep=source_config.get("delimiter"),
            engine="python",
            header=header,
            encoding=encoding,
        )
    elif reader_type == "excel":
        data = pd.read_excel(
            file_path,
            sheet_name=source_config.get("sheet_name", 0),
            header=header,
        )
    elif reader_type == "parquet":
        data = pd.read_parquet(file_path)
    elif reader_type == "json":
        data = pd.read_json(file_path, encoding=encoding)
    elif reader_type == "jsonl":
        data = pd.read_json(file_path, lines=True, encoding=encoding)
    elif reader_type == "xml":
        data = pd.read_xml(file_path, encoding=encoding)
    else:
        raise ValueError(f"No reader implemented for format: {file_format}")

    print(f"\nSource file read: {file_path.name}")
    print(f"Format: {file_format}")
    print(f"Rows: {len(data)}")
    print(f"Columns: {len(data.columns)}")
    if data.empty:
        print("Note: File contains zero data records.")

    return data


def ingest_delivery(delivery_directory, metadata_path=None):
    """Ingest every file matched by every source pattern in one delivery.

    Returns:
        results: one dictionary per ingested file, containing its DataFrame
                 and the source configuration that matched it.
        metadata: complete delivery metadata.

    A source entry can match one file (e.g. sales.csv) or several files
    (e.g. sales_*.csv). Each matched file is read separately.
    """
    delivery_directory = Path(delivery_directory).resolve()
    if not delivery_directory.is_dir():
        raise NotADirectoryError(
            f"Delivery directory not found: {delivery_directory}"
        )

    if metadata_path is None:
        metadata_path = delivery_directory / "metadata.yaml"

    metadata = load_metadata(metadata_path)
    results = []
    ingested_paths = set()

    for source in metadata["sources"]:
        source_id = source["source_id"]
        source_config = source["source_config"]
        pattern = source_config["file_pattern"]

        matched_files = sorted(
            path for path in delivery_directory.glob(pattern) if path.is_file()
        )
        if not matched_files:
            raise FileNotFoundError(
                f"No files matched pattern '{pattern}' for source '{source_id}'."
            )

        for matched_file in matched_files:
            source_file = matched_file.resolve()
            if source_file.parent != delivery_directory:
                raise ValueError(
                    f"Matched file '{matched_file.name}' is not directly "
                    "inside the delivery directory."
                )
            if source_file in ingested_paths:
                raise ValueError(
                    f"File '{matched_file.name}' matched more than one source "
                    "configuration. Make the patterns distinct."
                )
            ingested_paths.add(source_file)

            print("\n" + "=" * 55)
            print(f"Ingesting source: {source_id}")
            dataframe = read_data(source_file, source_config)
            file_format = _get_file_format(source_file, source_config)
            
            
            print("DEBUG - Returned type:", type(dataframe))
            print("DEBUG - Is DataFrame:", isinstance(dataframe, pd.DataFrame))

            results.append({
                "source_id": source_id,
                "file_name": source_file.name,
                "file_format": file_format,
                "dataframe": dataframe,
                "source_metadata": source,
            })

    print("\n" + "=" * 55)
    print("DELIVERY INGESTION COMPLETED")
    print(f"Delivery ID: {metadata['delivery_metadata'].get('delivery_id')}")
    print(f"Files processed: {len(results)}")
    print(f"Total records read: {sum(len(item['dataframe']) for item in results)}")

    return results, metadata


if __name__ == "__main__":

    delivery_folder = Path("sample_data")

    try:
        ingestion_results, delivery_metadata = ingest_delivery(
            delivery_folder
        )

        print("\n========== INGESTION SUCCESS ==========")

        print("\nDelivery Metadata:")
        print(delivery_metadata["delivery_metadata"])

        print("\n========== DATA PREVIEW ==========")

        for result in ingestion_results:

            print("\n" + "=" * 55)

            print("Source ID:", result["source_id"])
            print("File Name:", result["file_name"])
            print("File Format:", result["file_format"])

            dataframe = result["dataframe"]

            print("\nData Type:", type(dataframe))
            print("\nData Preview:")

            print(dataframe)   

            print("\nColumn Information:")
            print(dataframe.dtypes)

    except Exception as error:

        print("\n========== INGESTION FAILED ==========")
        print("Error:", error)
        raise
