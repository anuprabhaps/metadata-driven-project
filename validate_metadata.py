
import yaml

with open("sample_data/metadata.yaml", "r", encoding="utf-8") as file:
    metadata = yaml.safe_load(file)

print("Metadata loaded successfully!")

print("\nClient ID:")
print(metadata["client_info"]["client_id"])

print("\nSource Configuration:")
print(metadata["source_config"])

print("\nSchema Columns:")
for column in metadata["schema_definition"]["columns"]:
    print(column["name"], "->", column["data_type"])
