"""
FastAPI application for OCR Invoice Reader
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import tempfile
import shutil
import uuid
from pathlib import Path
from datetime import datetime
import io
import csv

from ocr_invoice_reader import __version__
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer
from ocr_invoice_reader.models.base import BaseDocument


# Storage for processing results (in production, use a database)
RESULTS_STORAGE = {}
TEMP_DIR = Path(tempfile.gettempdir()) / "ocr_invoice_reader"
TEMP_DIR.mkdir(exist_ok=True)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="OCR Invoice Reader API",
        description="Document information extraction API using PaddleOCR v4",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """API root endpoint"""
        return {
            "name": "OCR Invoice Reader API",
            "version": __version__,
            "status": "running",
            "endpoints": {
                "docs": "/docs",
                "health": "/health",
                "extract": "/api/v1/extract",
                "extract_enhanced": "/api/v1/extract/enhanced",
                "batch_extract": "/api/v1/extract/batch",
                "result": "/api/v1/result/{task_id}",
                "results": "/api/v1/results"
            }
        }

    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": __version__,
            "timestamp": datetime.now().isoformat()
        }

    @app.post("/api/v1/extract")
    async def extract_document(
        file: UploadFile = File(...),
        lang: str = Query("ch", description="OCR language (ch/en/japan/korean)"),
        use_gpu: bool = Query(False, description="Use GPU acceleration"),
        visualize: bool = Query(False, description="Generate visualization")
    ):
        """
        Extract structured information from a single document

        Returns the extraction result immediately (synchronous processing)
        """
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise HTTPException(400, "Invalid file type. Supported: PDF, JPG, JPEG, PNG")

        # Save uploaded file
        task_id = str(uuid.uuid4())
        temp_file = TEMP_DIR / f"{task_id}_{file.filename}"

        try:
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Process document
            extractor = DocumentExtractor(use_gpu=use_gpu, lang=lang)
            document = extractor.extract(str(temp_file), visualize=visualize)

            # Store result
            result = {
                "task_id": task_id,
                "status": "completed",
                "filename": file.filename,
                "document": document.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
            RESULTS_STORAGE[task_id] = result

            return result

        except Exception as e:
            raise HTTPException(500, f"Extraction failed: {str(e)}")

        finally:
            # Cleanup temp file
            if temp_file.exists():
                temp_file.unlink()

    @app.post("/api/v1/extract/enhanced")
    async def extract_enhanced(
        file: UploadFile = File(...),
        lang: str = Query("ch", description="OCR language"),
        use_gpu: bool = Query(False, description="Use GPU acceleration")
    ):
        """
        Extract with enhanced structure analysis (coordinate-based table detection)

        Returns detailed structure information including tables and regions
        """
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
            raise HTTPException(400, "Invalid file type")

        task_id = str(uuid.uuid4())
        temp_file = TEMP_DIR / f"{task_id}_{file.filename}"

        try:
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Process with enhanced analyzer
            analyzer = EnhancedStructureAnalyzer(use_gpu=use_gpu, lang=lang)
            result = analyzer.analyze(str(temp_file))

            # Convert regions to dict
            regions_data = []
            for region in result.get('regions', []):
                region_dict = {
                    'type': region.region_type,
                    'bbox': region.bbox,
                    'confidence': region.confidence,
                    'text': region.text
                }
                if hasattr(region, 'table_html') and region.table_html:
                    region_dict['table_html'] = region.table_html
                if hasattr(region, 'rows'):
                    region_dict['rows'] = region.rows
                if hasattr(region, 'columns'):
                    region_dict['columns'] = region.columns
                regions_data.append(region_dict)

            response = {
                "task_id": task_id,
                "status": "completed",
                "filename": file.filename,
                "method": result.get('method'),
                "regions": regions_data,
                "timestamp": datetime.now().isoformat()
            }

            RESULTS_STORAGE[task_id] = response
            return response

        except Exception as e:
            raise HTTPException(500, f"Enhanced extraction failed: {str(e)}")

        finally:
            if temp_file.exists():
                temp_file.unlink()

    @app.post("/api/v1/extract/batch")
    async def batch_extract(
        files: List[UploadFile] = File(...),
        lang: str = Query("ch", description="OCR language"),
        use_gpu: bool = Query(False, description="Use GPU acceleration"),
        background_tasks: BackgroundTasks = None
    ):
        """
        Batch extract from multiple documents

        Returns a task ID for tracking progress
        """
        if len(files) > 50:
            raise HTTPException(400, "Maximum 50 files per batch")

        task_id = str(uuid.uuid4())

        # Save files
        temp_files = []
        for file in files:
            if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                continue

            temp_file = TEMP_DIR / f"{task_id}_{file.filename}"
            with open(temp_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            temp_files.append(temp_file)

        if not temp_files:
            raise HTTPException(400, "No valid files uploaded")

        # Initialize task status
        RESULTS_STORAGE[task_id] = {
            "task_id": task_id,
            "status": "processing",
            "total_files": len(temp_files),
            "processed": 0,
            "documents": [],
            "timestamp": datetime.now().isoformat()
        }

        # Process in background
        def process_batch():
            try:
                extractor = DocumentExtractor(use_gpu=use_gpu, lang=lang)
                documents = []

                for idx, temp_file in enumerate(temp_files):
                    try:
                        doc = extractor.extract(str(temp_file), visualize=False)
                        documents.append(doc.to_dict())

                        # Update progress
                        RESULTS_STORAGE[task_id]["processed"] = idx + 1

                    except Exception as e:
                        print(f"Error processing {temp_file.name}: {e}")

                    finally:
                        if temp_file.exists():
                            temp_file.unlink()

                # Update final result
                RESULTS_STORAGE[task_id].update({
                    "status": "completed",
                    "documents": documents,
                    "completed_at": datetime.now().isoformat()
                })

            except Exception as e:
                RESULTS_STORAGE[task_id].update({
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.now().isoformat()
                })

        # Run in background
        background_tasks.add_task(process_batch)

        return {
            "task_id": task_id,
            "status": "processing",
            "message": f"Processing {len(temp_files)} files in background",
            "check_status": f"/api/v1/result/{task_id}"
        }

    @app.get("/api/v1/result/{task_id}")
    async def get_result(task_id: str):
        """Get extraction result by task ID"""
        if task_id not in RESULTS_STORAGE:
            raise HTTPException(404, "Task not found")

        return RESULTS_STORAGE[task_id]

    @app.get("/api/v1/results")
    async def list_results(limit: int = Query(10, ge=1, le=100)):
        """List recent extraction results"""
        results = list(RESULTS_STORAGE.values())
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return {
            "total": len(results),
            "results": results[:limit]
        }

    @app.get("/api/v1/result/{task_id}/csv")
    async def download_csv(
        task_id: str,
        mode: str = Query("summary", description="Export mode: summary or items")
    ):
        """Download extraction result as CSV"""
        if task_id not in RESULTS_STORAGE:
            raise HTTPException(404, "Task not found")

        result = RESULTS_STORAGE[task_id]

        if result.get('status') != 'completed':
            raise HTTPException(400, "Task not completed yet")

        # For batch results
        if 'documents' in result and isinstance(result['documents'], list):
            documents = [BaseDocument(**doc) for doc in result['documents']]
        # For single document result
        elif 'document' in result:
            documents = [BaseDocument(**result['document'])]
        else:
            raise HTTPException(400, "No document data found")

        # Generate CSV in memory
        output = io.StringIO()

        if mode == 'summary':
            rows = [doc.to_csv_row() for doc in documents]
        elif mode == 'items':
            rows = []
            for doc in documents:
                rows.extend(doc.to_csv_items())
        else:
            raise HTTPException(400, "Invalid mode. Use 'summary' or 'items'")

        if rows:
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        # Return as streaming response
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=extraction_{task_id}_{mode}.csv"
            }
        )

    @app.delete("/api/v1/result/{task_id}")
    async def delete_result(task_id: str):
        """Delete a stored result"""
        if task_id not in RESULTS_STORAGE:
            raise HTTPException(404, "Task not found")

        del RESULTS_STORAGE[task_id]
        return {"message": "Result deleted", "task_id": task_id}

    return app


# For running with uvicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
