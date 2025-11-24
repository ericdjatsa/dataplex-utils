import argparse
import sys
import yaml  # pip install pyyaml
from google.cloud import dataplex_v1
from google.protobuf.json_format import MessageToDict
from google.api_core import exceptions

def parse_arguments():
    """
    Configures and parses command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Extract the active Data Quality rules configuration from a Dataplex Scan.",
        epilog="Example:\n  python extract_dataplex_spec.py --project_id my-proj --scan_id my-scan --region us-central1",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--project_id", 
        required=True, 
        help="The Google Cloud Project ID."
    )
    parser.add_argument(
        "--scan_id", 
        required=True, 
        help="The ID of the Dataplex Data Quality Scan."
    )
    parser.add_argument(
        "--region", 
        required=True,
        default="us-central1", 
        help="The GCP region (default: us-central1)."
    )
    parser.add_argument(
        "--outputfile", 
        default="rules.yaml", 
        help="The filename for the generated YAML output (default: rules.yaml)."
    )

    return parser.parse_args()

def extract_spec(args):
    """
    Fetches the scan and extracts the current dataQualitySpec rules.
    """
    # 1. Initialize Client
    try:
        client = dataplex_v1.DataScanServiceClient()
    except Exception as e:
        print(f"[ERROR] Failed to initialize Dataplex Client: {e}")
        print("Tip: Run 'gcloud auth application-default login'")
        sys.exit(1)
    
    # 2. Construct Resource Name
    name = client.data_scan_path(args.project_id, args.region, args.scan_id)
    print(f"Reading configuration from: {name}...")
    
    try:
        # 3. Fetch the Scan
        # We use FULL view to ensure all spec details are present
        request = dataplex_v1.GetDataScanRequest(
            name=name,
            view=dataplex_v1.GetDataScanRequest.DataScanView.FULL
        )
        response = client.get_data_scan(request=request)
        
        # 4. Convert to Dict
        # preserving_proto_field_name=False ensures we get camelCase (e.g. nonNullExpectation)
        # which is required for the YAML config.
        scan_dict = MessageToDict(response._pb, preserving_proto_field_name=False)
        
        # 5. Extract 'dataQualitySpec' -> 'rules'
        dq_spec = scan_dict.get('dataQualitySpec', {})
        
        if not dq_spec:
             print("[ERROR] No 'dataQualitySpec' found. This might not be a Data Quality scan.")
             sys.exit(1)

        current_rules = dq_spec.get('rules', [])
        
        if not current_rules:
            print("[WARNING] The 'dataQualitySpec' exists but contains no rules.")
            print("If your rules are in a GCS file, this list will be empty.")
            return

        # 6. Save to YAML
        output_data = {'rules': current_rules}
        
        with open(args.outputfile, 'w') as f:
            yaml.dump(output_data, f, sort_keys=False, default_flow_style=False)
            
        print(f"[SUCCESS] Extracted {len(current_rules)} rules.")
        print(f"Configuration saved to: {args.outputfile}")

    except exceptions.NotFound:
        print(f"[ERROR] Scan not found: {args.scan_id} in {args.region}")
        print("Check your Scan ID and Region.")
        sys.exit(1)
    except exceptions.PermissionDenied:
        print(f"[ERROR] Permission denied for project: {args.project_id}")
        print("Check your IAM roles (Dataplex Viewer or DataScan Viewer required).")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    args = parse_arguments()
    extract_spec(args)