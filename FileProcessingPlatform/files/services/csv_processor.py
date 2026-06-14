import pandas as pd


def process_csv(file_instance):

    # file_obj = file_instance.file.open("rb")
    file_obj = file_instance.id
    # Donwload the file from S3.

    df = pd.read_csv(file_obj)

    total_rows = len(df)
    total_columns = len(df.columns)

    metadata = {
        "rows": total_rows,
        "columns": total_columns,
        "column_names": list(df.columns),
    }

    # Example:
    # store parsed rows into DB here

    file_instance.metadata = metadata
    file_instance.processing_status = "completed"

    file_instance.save(update_fields=["metadata", "processing_status"])

    return metadata