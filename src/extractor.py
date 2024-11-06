from pathlib import Path
from typing import Iterable
from datetime import datetime
from pypdf import PdfReader
from .helpers import Annotation



class Extractor:
    def __init__(self, pdf_file: Path) -> None:
        self.file = pdf_file
        self.reader = PdfReader(stream=self.file, strict=True)
        
    
    @property
    def annotations(self) -> Iterable[Annotation]:        
        for idx, page in enumerate(self.reader.pages):
            try :
                for annot in page["/Annots"] :
                    try:
                        obj = annot.get_object()
                        k = list(obj.keys())
                        assert obj['/Type'] == '/Annot'
                        if not '/Parent' in k:
                            continue # Every text-comment is nested

                        while '/Parent' in k: # bubble up
                            obj = obj['/Parent']
                            k = list(obj.keys())

                        content = obj['/Contents']
                        if not content:
                            continue # Perhaps just a comment-less highlight

                        # We gotta parse the date first. It'll look like this: D:20240912144917+02'00'
                        # It should look like this: 20240912144917+0200 for this format: %Y%m%d%H%M%SZ%z
                        raw_date = f'{obj["/M"]}'.split(':')[1].replace("'", '').replace('+', 'Z+').replace('-', 'Z-')

                        yield Annotation(page=idx+1, author=obj["/T"], timestamp=datetime.strptime(raw_date, '%Y%m%d%H%M%SZ%z'), comment=content)
                    except:
                        pass # The annotation could not be extracted
            except: 
                # there are no annotations on this page
                pass
    
    @property
    def text(self) -> Iterable[str]:
        for page in self.reader.pages:
            yield page.extract_text().strip()
