from typing import Optional, Any, Union, Callable
from transformers import LlamaTokenizer, AutoTokenizer
from PyPDF2 import PdfReader
import glob
class Docs:
    def __init__(self, docs_dir: Optional[str] = None, tokenizer: Union[Any, LlamaTokenizer, AutoTokenizer, Callable] = None, chunk_size : int = 1200, overlap : int = 0) -> None:
        if docs_dir:
            self.docs_dir = docs_dir
        else:
            self.docs_dir = './'
        self.pdf_files = glob.glob(self.docs_dir + '/' + '*.pdf')
        self.docs = []
        for pdf_file in self.pdf_files:
            self.docs.append({'text': self._pdf_to_text(pdf_file),
                              'file_dir': pdf_file})
        if tokenizer:
            self.tokenizer = tokenizer
        else:
            self.tokenizer = LlamaTokenizer.from_pretrained("TheBloke/wizard-vicuna-13B-HF")
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._split_text()

    def _pdf_to_text(self, pdf_file: str) -> str:
        with open(pdf_file, 'rb') as f:
            pdf = PdfReader(f)
            text = ''
            for page in pdf.pages:
                _text = page.extract_text()
                if _text:
                    text += _text
        return text

    def _split_text(self) -> None:
        for item in self.docs:
            doc = item['text']
            file_dir = item['file_dir']
            doc_tokenized = self.tokenizer._tokenize(doc)
            step = self.chunk_size - self.overlap
            doc_tokenized_splitted = [doc_tokenized[i:i + step] for i in range(0, len(doc_tokenized), step)]
            item_text_splitted = [self.tokenizer.convert_tokens_to_string(tokens) for tokens in doc_tokenized_splitted]
            item['text_splitted'] = item_text_splitted
        
    