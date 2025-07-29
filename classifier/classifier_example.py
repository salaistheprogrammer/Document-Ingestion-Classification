from transformers import LayoutLMv3Processor, LayoutLMv3ForSequenceClassification
from approach_two import extract_pdf
from pathlib import Path

processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)

lines = extract_pdf(Path(__file__).parent / "Linear resume.pdf")
print(lines)

codes = processor(images=lines[0]['image'], text=lines[0]['text'], boxes=lines[0]['bbox'], return_tensors='pt')

model = LayoutLMv3ForSequenceClassification.from_pretrained("microsoft/layoutlmv3-base")

outputs = model(**codes)
predicted_class = outputs.logits.argmax(-1)
print(predicted_class.item())
