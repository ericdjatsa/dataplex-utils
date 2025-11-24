# Dataplex Extract Data Quality Scan Rules

This is a tool to extract Data Quality Scan Rules from an existing Dataplex Data Quality Scan


## Prerequisites

1.  **Google Cloud SDK**: Ensure you have `gcloud` installed and authenticated.
2.  **Permissions**: You need appropriate IAM permissions to view Dataplex and BigQuery resources (e.g., `dataplex.datascans.describe`, `bigquery.tables.get`).
3.  **APIs**: Enable the Dataplex API and the BigQuery API in your Google Cloud project.

### 1. Extracting Rules from an Existing Scan

This repository includes a Python script to reads an existing Dataplex scan and generates a `rules.yaml` file from containing the data quality rules.

**A. Setup**

Install the required Python packages:
```bash
pip install -r requirements.txt
```

**B. Run the script**

Execute the script with your project, region, and scan ID.

```bash
python dataplex-extract-data-quality-rules.py \
  --project_id <your-project-id> \
  --region <gcp-region> \
  --scan_id <your-scan-id> \
  --outputfile my-rules.yaml
```

This will connect to Dataplex, fetch the specified scan's configuration, and save its rules to `my-rules.yaml`.

## `rules.yaml` File Reference

The `rules.yaml` file is the core of your data quality specification. It contains a list of rules to be applied to your table. The file must start with a `rules:` key.

### Rule Structure

Each rule in the list has the following components:

-   **`column`**: The name of the table column to which the rule applies.
-   **`dimension`**: The data quality dimension being measured (e.g., `COMPLETENESS`, `UNIQUENESS`, `VALIDITY`).
-   **`rule_type`**: The specific expectation for the rule (e.g., `nonNullExpectation`, `rangeExpectation`).
-   **`threshold`**: (Optional) A value between 0.0 and 1.0 representing the minimum percentage of rows that must pass the rule for the scan to succeed.
-   **`ignoreNull`**: (Optional) If `true`, `NULL` values are ignored when evaluating the rule.

### Rule Examples

Here are some common rule types.

#### Completeness: `nonNullExpectation`

This rule checks that a column does not contain `NULL` values. It is associated with the `COMPLETENESS` dimension.

```yaml
# Ensures that at least 99% of the values in the 'brand' column are not NULL.
- nonNullExpectation: {}
- nonNullExpectation: {}
  column: brand
  dimension: COMPLETENESS
  threshold: 0.99
```

#### Uniqueness: `uniquenessExpectation`

This rule checks that all values in a column are unique. It is associated with the `UNIQUENESS` dimension.

```yaml
# Ensures that every value in the 'id' column is unique.
- uniquenessExpectation: {}
- uniquenessExpectation: {}
  column: id
  dimension: UNIQUENESS
```

#### Validity: `rangeExpectation`

This rule checks that column values fall within a specified minimum and maximum. It is associated with the `VALIDITY` dimension.

```yaml
# Ensures that all non-null values in the 'cost' column are between the specified min and max.
- rangeExpectation:
    minValue: '0'
    maxValue: '557.1510021798313'
- rangeExpectation:
    minValue: '0.0082999997779726'
    maxValue: '557.1510021798313'
  column: cost
  ignoreNull: true
  dimension: VALIDITY
  threshold: 1.0
```

#### Validity: `setExpectation`

This rule checks that column values are members of a predefined set. It is associated with the `VALIDITY` dimension.

```yaml
# Ensures that all non-null values in the 'department' column are one of the specified values.
- setExpectation:
    values:
    - Women
    - Men
- setExpectation:
    values:
    - Women
    - Men
    - Living Room
  column: department
  ignoreNull: true
  dimension: VALIDITY
  threshold: 1.0
```

## Running the Scan

After extracting the rules, you can modify them and update the previous data quality scan with this command : 

    ```bash
    gcloud dataplex datascans update data-quality <your-existing-scan-id> \
      --location=<gcp-region> \
      --data-quality-spec-file=rules.yaml \
      --location=<gcp-region> \
    ```

Or create a new data quality scan with this command : 

    ```bash
    gcloud dataplex datascans create data-quality <your-new-scan-id> \
      --data-source-resource="//bigquery.googleapis.com/projects/<your-project-id>/datasets/<your-dataset>/tables/<your-table>" \
      --location=<gcp-region> \
      --data-quality-spec-file=rules.yaml
    ```

    Make sure you replace the placeholder values with your specific resource names.