"""
API Server CLI entry point
"""
import argparse
import sys


def main():
    """Main entry point for API server"""
    parser = argparse.ArgumentParser(
        prog="ocr-api",
        description="OCR Invoice Reader REST API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start API server
  ocr-api

  # Custom host and port
  ocr-api --host 0.0.0.0 --port 8080

  # Enable auto-reload for development
  ocr-api --reload

  # Access API documentation at http://localhost:8000/docs
        """
    )

    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind (default: 8000)'
    )
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload (development mode)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )

    args = parser.parse_args()

    try:
        import uvicorn
        from ocr_invoice_reader.api.app import app

        print("="*60)
        print("OCR Invoice Reader API Server")
        print("="*60)
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print(f"API Documentation: http://localhost:{args.port}/docs")
        print(f"ReDoc: http://localhost:{args.port}/redoc")
        print("="*60)

        uvicorn.run(
            "ocr_invoice_reader.api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1
        )

    except ImportError:
        print("\nError: FastAPI and uvicorn are required for API server")
        print("Install them with: pip install fastapi uvicorn[standard]")
        return 1

    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        return 0

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
