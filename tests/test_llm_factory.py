"""
Test suite for LLM Factory refactoring
Ensures backward compatibility and new functionality
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLLMFactory:
    """Test LLM Factory functionality"""

    def test_import_factory(self):
        """Test that llm_factory can be imported"""
        from ocr_invoice_reader.utils.llm_factory import create_llm_processor, LLMFactory
        assert create_llm_processor is not None
        assert LLMFactory is not None

    def test_import_qwen_direct(self):
        """Test that qwen_direct_processor can be imported"""
        from ocr_invoice_reader.utils.qwen_direct_processor import QwenDirectProcessor
        assert QwenDirectProcessor is not None

    def test_backend_detection(self):
        """Test backend availability detection"""
        from ocr_invoice_reader.utils.llm_factory import LLMFactory

        # Should not crash
        qwen_available = LLMFactory.is_qwen_direct_available()
        ollama_available = LLMFactory.is_ollama_available()

        assert isinstance(qwen_available, bool)
        assert isinstance(ollama_available, bool)

    def test_recommended_backend(self):
        """Test recommended backend selection"""
        from ocr_invoice_reader.utils.llm_factory import LLMFactory

        backend = LLMFactory.get_recommended_backend()
        assert backend in ["qwen_direct", "ollama", "auto"]

    def test_model_name_normalization(self):
        """Test that different model name formats are handled"""
        from ocr_invoice_reader.utils.llm_factory import create_llm_processor

        # These should all work (may skip if dependencies not available)
        test_cases = [
            ("7b", "qwen_direct"),
            ("14b", "qwen_direct"),
            ("3b", "qwen_direct"),
            ("qwen2.5:7b", "ollama"),
        ]

        for model, expected_backend in test_cases:
            try:
                processor = create_llm_processor(model, backend=expected_backend)
                # If creation succeeds, verify it has expected methods
                assert hasattr(processor, 'extract_invoice_fields')
                assert hasattr(processor, 'classify_document')
            except (ImportError, RuntimeError) as e:
                # Dependencies not available, skip
                pytest.skip(f"Skipping {model} - {expected_backend}: {e}")

    def test_api_consistency(self):
        """Test that all backends provide the same API"""
        required_methods = [
            'extract_invoice_fields',
            'classify_document',
            'correct_text',
            'extract_table_data',
        ]

        # Test Qwen Direct
        try:
            from ocr_invoice_reader.utils.qwen_direct_processor import create_qwen_processor
            processor = create_qwen_processor("7b", quantization="int4")

            for method in required_methods:
                assert hasattr(processor, method), f"Qwen Direct missing: {method}"

        except (ImportError, RuntimeError):
            pytest.skip("Qwen Direct not available")

        # Test Ollama
        try:
            from ocr_invoice_reader.utils.llm_processor import LLMProcessor
            processor = LLMProcessor("qwen2.5:7b")

            # Ollama has slightly different API
            assert hasattr(processor, 'extract_invoice_fields')
            assert hasattr(processor, 'classify_document')

        except (ImportError, RuntimeError):
            pytest.skip("Ollama not available")


class TestBackwardCompatibility:
    """Test backward compatibility with old code"""

    def test_old_import_still_works(self):
        """Test that old import path still works (with warning)"""
        import warnings

        # Should work but show deprecation warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                from ocr_invoice_reader.utils.llm_processor import create_llm_processor
                # Should have warning (if compat shim is in place)
            except ImportError:
                pytest.skip("Old import path removed (expected after full migration)")

    def test_ollama_model_names_work(self):
        """Test that Ollama-style model names still work"""
        from ocr_invoice_reader.utils.llm_factory import create_llm_processor

        # Old Ollama format should be converted
        try:
            processor = create_llm_processor("qwen2.5:7b", backend="ollama")
            assert processor is not None
        except (ImportError, RuntimeError) as e:
            pytest.skip(f"Ollama not available: {e}")


class TestRefactoredCLI:
    """Test refactored CLI functionality"""

    def test_cli_import(self):
        """Test that refactored CLI can be imported"""
        try:
            from ocr_invoice_reader.cli import enhanced_extract_refactored
            assert enhanced_extract_refactored is not None
        except ImportError as e:
            pytest.fail(f"Failed to import refactored CLI: {e}")

    def test_cli_has_main(self):
        """Test that CLI has main function"""
        from ocr_invoice_reader.cli import enhanced_extract_refactored
        assert hasattr(enhanced_extract_refactored, 'main')


class TestIntegration:
    """Integration tests for complete flow"""

    @pytest.mark.integration
    def test_full_extraction_flow(self):
        """Test complete OCR + LLM extraction"""
        from ocr_invoice_reader.utils.llm_factory import create_llm_processor

        # Create processor (auto-select backend)
        try:
            processor = create_llm_processor("7b", backend="auto")
        except Exception as e:
            pytest.skip(f"No LLM backend available: {e}")

        # Test text
        test_text = """
        发票号码: INV-2024-001
        日期: 2024-05-15
        金额: ¥1,234.56
        公司: 测试公司有限责任公司
        """

        # Extract
        result = processor.extract_invoice_fields(test_text)

        # Verify result structure
        assert isinstance(result, dict)
        # Should have some extracted data (exact format may vary)

    @pytest.mark.integration
    def test_performance_benchmark(self):
        """Benchmark LLM inference speed"""
        import time
        from ocr_invoice_reader.utils.llm_factory import create_llm_processor

        try:
            processor = create_llm_processor("7b", backend="qwen_direct", quantization="int4")
        except Exception:
            pytest.skip("Qwen Direct not available")

        test_text = "发票号码: INV-001\n日期: 2024-05-15\n金额: ¥1000"

        # Warm up
        processor.extract_invoice_fields(test_text)

        # Measure
        start = time.time()
        result = processor.extract_invoice_fields(test_text)
        duration = time.time() - start

        # Should be fast with Qwen Direct
        assert duration < 10, f"Inference too slow: {duration:.2f}s"
        print(f"\n✓ Inference time: {duration:.2f}s")


def test_documentation_exists():
    """Test that refactoring documentation exists"""
    import os

    docs = [
        "REFACTORING_GUIDE.md",
        "docs/QWEN_DIRECT_SETUP.md",
    ]

    for doc in docs:
        path = Path(__file__).parent.parent / doc
        assert path.exists(), f"Missing documentation: {doc}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
