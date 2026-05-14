"""
Example: REST API Client Usage

This example demonstrates how to use the OCR Invoice Reader REST API.
"""
import requests
import time
from pathlib import Path
from typing import List, Dict, Any


class OCRInvoiceClient:
    """Python client for OCR Invoice Reader API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check if API is healthy"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def extract_single(
        self,
        file_path: str,
        lang: str = "ch",
        use_gpu: bool = False,
        visualize: bool = False
    ) -> Dict[str, Any]:
        """
        Extract from single document (synchronous)

        Args:
            file_path: Path to document file
            lang: OCR language (ch/en/japan/korean)
            use_gpu: Use GPU acceleration
            visualize: Generate visualization

        Returns:
            Extraction result with document data
        """
        url = f"{self.base_url}/api/v1/extract"

        with open(file_path, "rb") as f:
            files = {"file": f}
            params = {
                "lang": lang,
                "use_gpu": use_gpu,
                "visualize": visualize
            }
            response = self.session.post(url, files=files, params=params)
            response.raise_for_status()
            return response.json()

    def extract_enhanced(
        self,
        file_path: str,
        lang: str = "ch",
        use_gpu: bool = False
    ) -> Dict[str, Any]:
        """
        Extract with enhanced structure analysis

        Args:
            file_path: Path to document file
            lang: OCR language
            use_gpu: Use GPU acceleration

        Returns:
            Enhanced extraction result with regions and tables
        """
        url = f"{self.base_url}/api/v1/extract/enhanced"

        with open(file_path, "rb") as f:
            files = {"file": f}
            params = {"lang": lang, "use_gpu": use_gpu}
            response = self.session.post(url, files=files, params=params)
            response.raise_for_status()
            return response.json()

    def extract_batch(
        self,
        file_paths: List[str],
        lang: str = "ch",
        use_gpu: bool = False,
        wait: bool = True,
        poll_interval: int = 2
    ) -> Dict[str, Any]:
        """
        Extract from multiple documents (asynchronous)

        Args:
            file_paths: List of file paths
            lang: OCR language
            use_gpu: Use GPU acceleration
            wait: Wait for completion
            poll_interval: Polling interval in seconds

        Returns:
            Batch extraction result
        """
        url = f"{self.base_url}/api/v1/extract/batch"

        files = [("files", open(fp, "rb")) for fp in file_paths]
        params = {"lang": lang, "use_gpu": use_gpu}

        try:
            response = self.session.post(url, files=files, params=params)
            response.raise_for_status()
            result = response.json()

            if wait:
                return self.wait_for_completion(
                    result["task_id"],
                    poll_interval=poll_interval
                )
            return result

        finally:
            # Close file handles
            for _, file_obj in files:
                file_obj.close()

    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 2,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Wait for batch processing to complete

        Args:
            task_id: Task ID to monitor
            poll_interval: Polling interval in seconds
            timeout: Timeout in seconds

        Returns:
            Final result

        Raises:
            TimeoutError: If processing exceeds timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.get_result(task_id)

            status = result.get("status")
            if status == "completed":
                return result
            elif status == "failed":
                error = result.get("error", "Unknown error")
                raise Exception(f"Processing failed: {error}")

            # Show progress
            if "processed" in result and "total_files" in result:
                processed = result["processed"]
                total = result["total_files"]
                print(f"Progress: {processed}/{total} ({processed/total*100:.1f}%)")

            time.sleep(poll_interval)

        raise TimeoutError(f"Processing timeout after {timeout}s")

    def get_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get result by task ID

        Args:
            task_id: Task ID

        Returns:
            Result data
        """
        url = f"{self.base_url}/api/v1/result/{task_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def download_csv(
        self,
        task_id: str,
        output_path: str,
        mode: str = "summary"
    ) -> str:
        """
        Download result as CSV

        Args:
            task_id: Task ID
            output_path: Output file path
            mode: Export mode ('summary' or 'items')

        Returns:
            Output file path
        """
        url = f"{self.base_url}/api/v1/result/{task_id}/csv"
        params = {"mode": mode}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        return output_path

    def list_results(self, limit: int = 10) -> Dict[str, Any]:
        """
        List recent results

        Args:
            limit: Maximum results to return

        Returns:
            List of results
        """
        url = f"{self.base_url}/api/v1/results"
        params = {"limit": limit}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def delete_result(self, task_id: str) -> Dict[str, Any]:
        """
        Delete a result

        Args:
            task_id: Task ID to delete

        Returns:
            Deletion confirmation
        """
        url = f"{self.base_url}/api/v1/result/{task_id}"
        response = self.session.delete(url)
        response.raise_for_status()
        return response.json()


# Example usage functions

def example_health_check():
    """Check if API is running"""
    print("\n" + "=" * 60)
    print("Example 1: Health Check")
    print("=" * 60)

    client = OCRInvoiceClient()

    try:
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
        print(f"✓ Version: {health['version']}")
        print(f"✓ Timestamp: {health['timestamp']}")
    except Exception as e:
        print(f"✗ API not available: {e}")
        print("\nMake sure to start the API server first:")
        print("  ocr-api")


def example_single_extraction():
    """Extract from single document"""
    print("\n" + "=" * 60)
    print("Example 2: Single Document Extraction")
    print("=" * 60)

    client = OCRInvoiceClient()

    try:
        # Extract document
        result = client.extract_single(
            "invoice.pdf",
            lang="ch",
            use_gpu=False
        )

        task_id = result["task_id"]
        document = result["document"]

        print(f"✓ Task ID: {task_id}")
        print(f"✓ Document Type: {document['document_type']}")
        print(f"✓ Document Number: {document.get('document_number', 'N/A')}")
        print(f"✓ Total Amount: {document.get('total_amount', 'N/A')} {document['currency']}")
        print(f"✓ Confidence: {document['confidence']:.1%}")

        # Download CSVs
        summary_csv = client.download_csv(task_id, "output/result_summary.csv", mode="summary")
        items_csv = client.download_csv(task_id, "output/result_items.csv", mode="items")

        print(f"\n✓ Summary CSV: {summary_csv}")
        print(f"✓ Items CSV: {items_csv}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_enhanced_extraction():
    """Extract with enhanced structure analysis"""
    print("\n" + "=" * 60)
    print("Example 3: Enhanced Structure Extraction")
    print("=" * 60)

    client = OCRInvoiceClient()

    try:
        result = client.extract_enhanced(
            "invoice.pdf",
            lang="ch",
            use_gpu=False
        )

        print(f"✓ Method: {result['method']}")
        print(f"✓ Regions detected: {len(result['regions'])}")

        # Show region types
        region_types = {}
        for region in result['regions']:
            r_type = region['type']
            region_types[r_type] = region_types.get(r_type, 0) + 1

        print("\nRegion breakdown:")
        for r_type, count in region_types.items():
            print(f"  - {r_type}: {count}")

        # Show tables
        tables = [r for r in result['regions'] if r['type'] == 'table']
        if tables:
            print(f"\n✓ Found {len(tables)} table(s)")
            for idx, table in enumerate(tables, 1):
                print(f"  Table {idx}: {table.get('rows', '?')} rows × {table.get('columns', '?')} cols")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_batch_extraction():
    """Batch extract from multiple documents"""
    print("\n" + "=" * 60)
    print("Example 4: Batch Extraction")
    print("=" * 60)

    client = OCRInvoiceClient()

    try:
        # Find all PDF files
        pdf_files = list(Path("invoices/").glob("*.pdf"))[:5]  # Limit to 5 files

        if not pdf_files:
            print("✗ No PDF files found in invoices/ directory")
            return

        print(f"Processing {len(pdf_files)} files...")

        # Start batch processing
        result = client.extract_batch(
            [str(f) for f in pdf_files],
            lang="ch",
            use_gpu=False,
            wait=True  # Wait for completion
        )

        print(f"\n✓ Task completed!")
        print(f"✓ Processed: {len(result['documents'])} documents")

        # Download batch CSV
        task_id = result["task_id"]
        batch_csv = client.download_csv(task_id, "output/batch_summary.csv", mode="summary")
        print(f"✓ Batch CSV: {batch_csv}")

        # Show summary
        print("\nDocuments processed:")
        for doc in result['documents']:
            doc_num = doc.get('document_number', 'N/A')
            amount = doc.get('total_amount', 'N/A')
            print(f"  - {doc_num}: {amount} {doc['currency']}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_list_results():
    """List recent results"""
    print("\n" + "=" * 60)
    print("Example 5: List Recent Results")
    print("=" * 60)

    client = OCRInvoiceClient()

    try:
        results = client.list_results(limit=5)

        print(f"Total results: {results['total']}")
        print(f"Showing: {len(results['results'])}\n")

        for result in results['results']:
            task_id = result['task_id']
            status = result['status']
            timestamp = result.get('timestamp', 'N/A')
            print(f"  [{status}] {task_id} - {timestamp}")

    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║        OCR Invoice Reader - REST API Client Examples      ║
╚════════════════════════════════════════════════════════════╝

Before running these examples:
  1. Start the API server: ocr-api
  2. Ensure you have test PDF files ready
  3. Install requests: pip install requests
    """)

    # Run examples
    example_health_check()

    # Uncomment to run other examples:
    # example_single_extraction()
    # example_enhanced_extraction()
    # example_batch_extraction()
    # example_list_results()

    print("\n" + "=" * 60)
    print("To run the other examples:")
    print("  1. Uncomment the example functions above")
    print("  2. Prepare test PDF files")
    print("  3. Start API server: ocr-api")
    print("  4. Run: python examples/api_client_example.py")
    print("=" * 60)
