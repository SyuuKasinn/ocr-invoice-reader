# OCR Enhancement Proposal

## Current Issues Analysis

Based on results in `results/20260512_151320/`:

### Issue 1: Word Segmentation
- **Problem**: "INTERNATIONALEXPRESSWAYBILL" (no spaces)
- **Impact**: Unreadable, hard to process
- **Frequency**: High in headers/titles

### Issue 2: Character Recognition Errors
- **Problem**: "EXPRESS" → "PRESS", "From" → "Frロm"
- **Impact**: Data quality, search failures
- **Frequency**: Medium-High

### Issue 3: Mixed Language Confusion
- **Problem**: Japanese characters in English words ("CONN日N!")
- **Impact**: Wrong language detection in mixed contexts
- **Frequency**: High in multilingual documents

### Issue 4: Over-fragmentation
- **Problem**: 272 detections on single page, should be ~50-80
- **Impact**: Difficult to reconstruct logical reading order
- **Frequency**: Very High

### Issue 5: Lost Table Structure
- **Problem**: Table cells detected as isolated text blocks
- **Impact**: Cannot extract structured data (key-value pairs)
- **Frequency**: Critical for invoice processing

## Mainstream Solutions

### Solution 1: Layout Analysis (Recommended)
**Technology**: LayoutLMv3 / Donut / Surya

#### A. LayoutLMv3 (Microsoft)
```bash
pip install transformers layoutparser
```

**Capabilities**:
- Document layout understanding
- Table structure recognition
- Reading order detection
- Form key-value extraction

**Implementation**:
```python
from transformers import LayoutLMv3ForTokenClassification
from layoutparser import PaddleDetectionLayoutModel

# Layout detection
layout_model = PaddleDetectionLayoutModel('lp://PubLayNet/ppyolov2_r50vd_dcn_365e')
layout = layout_model.detect(image)

# Classify regions: title, text, table, figure
for block in layout:
    if block.type == 'table':
        # Use specialized table OCR
        table_ocr(block)
    else:
        # Standard OCR
        text_ocr(block)
```

**Advantages**:
- Industry standard for document understanding
- Handles complex layouts (invoices, forms)
- Pre-trained on document datasets
- Open source

**Disadvantages**:
- Requires additional dependencies
- Higher computational cost
- Learning curve for integration

#### B. Donut (Naver Clova)
```bash
pip install donut-python
```

**Capabilities**:
- OCR-free document understanding
- Direct image-to-text without OCR
- Built-in document structure understanding

**Implementation**:
```python
from donut import DonutModel

model = DonutModel.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
result = model.inference(
    image=invoice_image,
    prompt="<s_docvqa><s_question>Extract all fields from this invoice</s_question><s_answer>"
)
```

**Advantages**:
- State-of-the-art accuracy
- No separate OCR needed
- Understands document semantics

**Disadvantages**:
- Requires GPU (large model)
- May need fine-tuning for specific formats
- Slower than traditional OCR

### Solution 2: Advanced Post-processing
**Technology**: SymSpell + Language Models

#### A. SymSpell for Fast Correction
```bash
pip install symspellpy
```

**Implementation**:
```python
from symspellpy import SymSpell, Verbosity

sym_spell = SymSpell(max_dictionary_edit_distance=2)
sym_spell.load_dictionary("frequency_dictionary_en_82_765.txt", 0, 1)

def correct_with_symspell(text):
    suggestions = sym_spell.lookup(text, Verbosity.CLOSEST, max_edit_distance=2)
    if suggestions:
        return suggestions[0].term
    return text

# Fix: "PRESS" → "EXPRESS", "CUStONEr" → "Customer"
```

**Advantages**:
- Very fast (1M words/sec)
- Low memory usage
- Language agnostic

#### B. Word Segmentation
```bash
pip install wordninja
```

**Implementation**:
```python
import wordninja

# Fix: "INTERNATIONALEXPRESSWAYBILL" → ["INTERNATIONAL", "EXPRESS", "WAYBILL"]
words = wordninja.split("INTERNATIONALEXPRESSWAYBILL")
result = " ".join(words)  # "INTERNATIONAL EXPRESS WAYBILL"
```

**Advantages**:
- Simple integration
- Works well for English
- No training required

### Solution 3: LLM-based Intelligent Correction
**Technology**: Claude API / GPT-4 Vision / Local LLMs

#### A. Cloud API Approach (Best Quality)
```bash
pip install anthropic
```

**Implementation**:
```python
import anthropic
from PIL import Image
import base64

client = anthropic.Anthropic(api_key="your-api-key")

def intelligent_ocr_correction(image_path, ocr_results):
    # Load image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # Create prompt
    ocr_text = "\n".join([r['text'] for r in ocr_results])
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": f"""This is an invoice/waybill document. The OCR results have errors:

OCR Output:
{ocr_text}

Please:
1. Fix character recognition errors (e.g., "PRESS" should be "EXPRESS")
2. Add proper word spacing (e.g., "INTERNATIONALEXPRESSWAYBILL" → "INTERNATIONAL EXPRESS WAYBILL")
3. Fix mixed language errors (e.g., "Frロm" → "From")
4. Structure the output as JSON with corrected fields

Return only the corrected JSON without explanation."""
                }
            ]
        }]
    )
    
    return message.content[0].text
```

**Advantages**:
- Highest accuracy (understands context)
- Can extract structured data automatically
- Handles complex layouts
- Multi-language support

**Disadvantages**:
- Requires API subscription
- Cost per request
- Internet dependency

#### B. Local LLM Approach (Free)
```bash
pip install llama-cpp-python
```

**Implementation**:
```python
from llama_cpp import Llama

# Use local models like Llama-3.2-Vision or Qwen2-VL
llm = Llama(model_path="./models/llama-3.2-11b-vision.gguf", n_ctx=4096)

def local_llm_correction(ocr_results):
    prompt = f"""Fix OCR errors in this invoice text:
    
{ocr_results}

Rules:
- Fix spelling: PRESS → EXPRESS
- Add spaces: INTERNATIONALEXPRESSWAYBILL → INTERNATIONAL EXPRESS WAYBILL  
- Remove wrong characters: Frロm → From
- Keep numbers unchanged

Output corrected text only:"""

    response = llm(prompt, max_tokens=2048)
    return response['choices'][0]['text']
```

**Advantages**:
- No API costs
- Privacy (local processing)
- Customizable

**Disadvantages**:
- Requires powerful GPU
- Lower accuracy than cloud APIs
- Model size (10-70GB)

### Solution 4: Table-Specific Recognition
**Technology**: Table Transformer + CascadeTabNet

```bash
pip install table-transformer
```

**Implementation**:
```python
from table_transformer import TableTransformerForObjectDetection
from transformers import AutoImageProcessor

# Detect table structure
processor = AutoImageProcessor.from_pretrained("microsoft/table-transformer-detection")
model = TableTransformerForObjectDetection.from_pretrained("microsoft/table-transformer-detection")

# Extract table cells
def extract_table_structure(image):
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    
    # Get bounding boxes for table, rows, columns
    table_structure = processor.post_process_object_detection(outputs)
    
    # Run OCR on each cell
    for cell in table_structure['cells']:
        cell_image = crop_image(image, cell['bbox'])
        cell_text = ocr.recognize(cell_image)
        cell['text'] = cell_text
    
    # Reconstruct as structured data
    return build_table(table_structure)
```

**Advantages**:
- Purpose-built for tables
- Preserves structure
- Better than generic OCR for invoices

### Solution 5: Multi-Model Ensemble
**Combine multiple approaches for best results**

```python
class EnhancedInvoiceOCR:
    def __init__(self):
        self.paddleocr = PaddleOCR()           # Primary OCR
        self.layout_model = LayoutDetector()   # Layout analysis
        self.table_model = TableExtractor()    # Table recognition
        self.text_corrector = SymSpellCorrector()
        self.llm_corrector = ClaudeCorrector() # Final pass
    
    def process(self, image_path):
        # Step 1: Layout analysis
        layout = self.layout_model.detect(image_path)
        
        # Step 2: Region-specific OCR
        results = []
        for region in layout:
            if region.type == 'table':
                data = self.table_model.extract(region.crop)
            else:
                data = self.paddleocr.ocr(region.crop)
            results.append(data)
        
        # Step 3: Fast correction
        for item in results:
            item['text'] = self.text_corrector.correct(item['text'])
        
        # Step 4: LLM intelligent correction (optional)
        if self.use_llm:
            results = self.llm_corrector.correct(image_path, results)
        
        return results
```

## Recommended Implementation Plan

### Phase 1: Quick Wins (1-2 days)
1. **Add word segmentation** using `wordninja`
2. **Add SymSpell correction** for fast spelling fixes
3. **Improve text merging** logic to reduce fragmentation

**Expected Improvement**: 30-40% reduction in errors

### Phase 2: Layout Understanding (3-5 days)
1. **Integrate layout detection** (PaddleOCR's layout analysis or LayoutParser)
2. **Separate table vs text processing**
3. **Improve reading order detection**

**Expected Improvement**: 50-60% better structure

### Phase 3: LLM Enhancement (2-3 days)
1. **Add Claude API integration** (optional, for high-value documents)
2. **Create prompt templates** for different document types
3. **Add confidence-based LLM triggering** (only for low-confidence results)

**Expected Improvement**: 70-90% accuracy on complex documents

### Phase 4: Fine-tuning (Ongoing)
1. **Collect error samples**
2. **Build custom dictionaries** for domain-specific terms
3. **Train custom models** on your invoice formats

## Cost-Benefit Analysis

| Solution | Cost | Implementation | Accuracy Gain | Speed Impact |
|----------|------|----------------|---------------|--------------|
| Word Segmentation | Free | 2 hours | +15% | Negligible |
| SymSpell | Free | 4 hours | +20% | +0.1s/page |
| Layout Analysis | Free | 2 days | +30% | +0.5s/page |
| Table Transformer | Free | 3 days | +40% tables | +1s/page |
| Claude API | $0.01-0.05/page | 1 day | +60% | +2s/page |
| Local LLM | Free (GPU) | 3 days | +40% | +5s/page |
| Full Ensemble | Mixed | 2 weeks | +80% | +3s/page |

## Quick Start: Minimal Enhancement

Add these to `ocr_reader.py` immediately:

```python
# Install: pip install wordninja symspellpy

import wordninja
from symspellpy import SymSpell

class EnhancedTextCorrector(TextCorrector):
    def __init__(self):
        super().__init__()
        
        # Word segmentation
        self.use_segmentation = True
        
        # SymSpell setup
        self.sym_spell = SymSpell(max_dictionary_edit_distance=2)
        # Download dictionary from: https://github.com/wolfgarbe/SymSpell
        self.sym_spell.load_dictionary("frequency_dictionary_en_82_765.txt", 0, 1)
    
    def correct_text(self, text, lang_hint='en'):
        # 1. Word segmentation for concatenated text
        if self.use_segmentation and text.isupper() and len(text) > 15:
            words = wordninja.split(text.lower())
            text = " ".join([w.upper() for w in words])
        
        # 2. SymSpell correction
        if lang_hint == 'en':
            suggestions = self.sym_spell.lookup(text, Verbosity.CLOSEST, max_edit_distance=2)
            if suggestions:
                text = suggestions[0].term
        
        # 3. Existing correction logic
        text = super().correct_text(text, lang_hint)
        
        return text
```

This provides immediate improvements with minimal effort.

## References

1. **LayoutLMv3**: https://github.com/microsoft/unilm/tree/master/layoutlmv3
2. **Donut**: https://github.com/clovaai/donut
3. **Table Transformer**: https://github.com/microsoft/table-transformer
4. **SymSpell**: https://github.com/wolfgarbe/SymSpell
5. **wordninja**: https://github.com/keredson/wordninja
6. **Surya OCR**: https://github.com/VikParuchuri/surya (newer alternative)
7. **PaddleOCR Layout**: https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.8/ppstructure/README.md

## Conclusion

**Recommended immediate action**: Implement Phase 1 (word segmentation + SymSpell) for quick wins, then evaluate if Phase 2/3 are needed based on your accuracy requirements and budget.

For production invoice processing, the **full ensemble approach** with Claude API for complex cases provides the best ROI.
