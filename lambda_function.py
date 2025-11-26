import json
import os

import boto3


# Re‑use the same S3 client across invocations
s3 = boto3.client("s3")

# Name of the processed bucket. You can override this with a Lambda env var.
PROCESSED_BUCKET = os.environ.get("PROCESSED_BUCKET", "josue-processed-data")


def infer_frequency_from_name(key: str) -> str:
    """Infer data frequency from the object key/filename."""
    key_lower = key.lower()
    if "annual" in key_lower:
        return "annual"
    if "quarter" in key_lower or "qtr" in key_lower:
        return "quarterly"
    if "month" in key_lower:
        return "monthly"
    if "week" in key_lower:
        return "weekly"
    if "day" in key_lower or "daily" in key_lower:
        return "daily"
    if "description" in key_lower:
        return "description/meta"
    return "unknown"


def lambda_handler(event, context):
    """Lambda entry‑point.

    This function is triggered by an S3 event whenever a CSV file is uploaded
    to the *raw* bucket. It reads the object, performs a light‑weight
    inspection (header + row count + size), infers the data frequency from
    the key name, and writes a summary JSON file into the *processed*
    bucket under the `summaries/` prefix.
    """

    # 1. Get bucket + key from the event
    record = event["Records"][0]
    source_bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    # 2. Download the object
    obj = s3.get_object(Bucket=source_bucket, Key=key)
    size_bytes = obj["ContentLength"]
    body = obj["Body"].read().decode("utf-8", errors="ignore")

    # 3. Parse CSV header + row count (very simple)
    lines = [line for line in body.splitlines() if line.strip()]
    header: list[str] = []
    row_count = 0
    if lines:
        header = [col.strip() for col in lines[0].split(",")]
        row_count = max(len(lines) - 1, 0)

    # 4. Infer frequency from filename (day/week/month/etc.)
    frequency = infer_frequency_from_name(key)

    # 5. Build summary JSON
    summary = {
        "source_bucket": source_bucket,
        "file_name": key,
        "size_bytes": size_bytes,
        "row_count": row_count,
        "header_columns": header,
        "inferred_frequency": frequency,
    }

    # 6. Save to processed bucket under summaries/
    base_name = os.path.basename(key)
    summary_key = f"summaries/{base_name}.summary.json"

    s3.put_object(
        Bucket=PROCESSED_BUCKET,
        Key=summary_key,
        Body=json.dumps(summary, indent=2),
        ContentType="application/json",
    )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "processed", "summary_key": summary_key}),
    }
