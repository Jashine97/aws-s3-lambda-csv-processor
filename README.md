# SARB CSV → AWS S3 + Lambda Summaries

Small AWS project that shows how to take raw CSV files from the South African
Reserve Bank (SARB), drop them into an S3 bucket, and have a Lambda function
automatically create a light‑weight JSON summary for each upload.

## Architecture

See `architecture/aws_architecture.md` for the simple ASCII diagram of the flow:

- **S3 raw bucket** – e.g. `josue-raw-data`
- **Lambda function** – `sarb_csv_summary`
- **S3 processed bucket** – e.g. `josue-processed-data` under the `summaries/` prefix

## Lambda function

The implementation lives in `src/lambda_function.py`.

High‑level behaviour:

1. Triggered by an S3 `ObjectCreated` event from the *raw* bucket.
2. Downloads the CSV file.
3. Computes:
   - file size in bytes
   - header column names
   - simple row count (number of non‑empty lines minus the header)
   - inferred frequency from the filename (annual, quarterly, monthly,
     weekly, daily, etc.).
4. Writes a JSON summary to the *processed* bucket as
   `summaries/<original_name>.summary.json`.

Example output for `sarb_day.csv` can be found in
`data/processed_examples/sarb_day.csv.summary.json`.
