from ingestion import ingest_delivery

try:
    dataframe, metadata = ingest_delivery("sample_data")

    print("\n========== INGESTION SUCCESS ==========")

    print("\nMetadata:")
    print(metadata)

    print("\nData Preview:")
    print(dataframe.head())

    print("\nTotal Records:", len(dataframe))

    print("\nColumns:")
    print(dataframe.columns.tolist())

    print("\nData Types:")
    print(dataframe.dtypes)

except Exception as error:
    print("\n========== INGESTION FAILED ==========")
    print("Error:", error)