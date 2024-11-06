from .helpers import ProcessedPdf
from typing import Iterable, Self
from re import match, RegexFlag, sub
from dataclasses import dataclass

@dataclass
class TocEntry:
    key: str
    title: str
    pdf: ProcessedPdf



class MarkdownWithToc:
    def __init__(self) -> None:
        self.pdfs: list[ProcessedPdf] = []
    
    @property
    def yaml_header(self) -> str:
        return """---
geometry: "left=2.5cm,right=2.5cm,top=2cm,bottom=2cm,a4paper"
output: pdf_document
---
"""

    def add_processed(self, procPdf: ProcessedPdf|None) -> Self:
        if isinstance(procPdf, ProcessedPdf):
            self.pdfs.append(procPdf)
        return self
    
    def add_all_processed(self, procPdfs: Iterable[ProcessedPdf|None]) -> Self:
        for pdf in procPdfs:
            self.add_processed(procPdf=pdf)
        
        return self
    

    def generate_toc_entries(self) -> dict[ProcessedPdf, TocEntry]:
        m = dict()

        for pdf in self.pdfs:
            title = pdf.title.strip()
            key = sub('[^0-9a-zA-Z]+', '-', title).strip('-').lower()
            m[pdf] = TocEntry(key=key, title=title, pdf=pdf)
        
        return m
    
    def generate_toc(self, entries: dict[ProcessedPdf, TocEntry], group_num_letters = 5) -> str:
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        groups: list[tuple[str, str, list[tuple[ProcessedPdf, TocEntry]]]] = []
        # First, append a group for non-alphanumerical items
        temp = list([item for item in entries.items() if item[0].has_annotations and bool(match('^[^a-z]', item[1].title, RegexFlag.IGNORECASE))])
        if len(temp) > 0:
            used_digits = sorted(set([a[1].title[0] for a in temp]))
            groups.append((', '.join(used_digits), None, temp))
        

        # Now for the Alpha-groups:
        offset = 0
        while offset < len(letters) - 1:
            first_letter = letters[offset]
            take_num_letters = group_num_letters if (offset + 2*group_num_letters) < len(letters) else len(letters) - offset
            last_letter = letters[offset + take_num_letters - 1]
            temp = list([item for item in entries.items() if item[0].has_annotations and bool(match(f'^[{first_letter}-{last_letter}]', item[1].title, RegexFlag.IGNORECASE))])
            if len(temp) > 0:
                groups.append((first_letter, last_letter, temp))
            offset += take_num_letters


        # The no-comments group:
        temp = list([item for item in entries.items() if not item[0].has_annotations])
        if len(temp) > 0:
            groups.append(('PDFs without Annotations / Comments', None, temp))


        head = f'# Table Of Contents\n-----------\n'
        chunks: list[str] = []
        for group in groups:
            left, right, items = group
            chunks.append(f'\n## {left}{'' if right is None else f" &mdash; {right}"}\n')
            text_entries = [f'* {tpl[1].title if not tpl[0].has_annotations else f"[{tpl[1].title}](#{tpl[1].key})"}' for tpl in items]
            chunks.append("\n".join(text_entries))
        
        return f'{head}\n\n{"\n".join(chunks)}'


    def generate_annotation(self, pdf: ProcessedPdf, toc_entry: TocEntry) -> str:
        head = f'## {pdf.title} <a name="{toc_entry.key}"></a>'
        annots = [f'\n### Page {annot.page}, {annot.author} [{annot.timestamp.strftime('%Y-%m-%d, %H:%M:%S')}]\n\n{annot.comment}' for annot in pdf.annotations]
        return f'{head}\n\n{"\n".join(annots)}'
    

    def generate_document(self, generate_md_toc: bool=True) -> str:
        """
        Generates a Markdown document with Table of contents.
        """
        entries = self.generate_toc_entries()
        toc = '' if not generate_md_toc else self.generate_toc(entries=entries)

        chunks: list[str] = []
        for (pdf, entry) in entries.items():
            if not pdf.has_annotations:
                continue
            chunks.append(self.generate_annotation(pdf=pdf, toc_entry=entry))
        
        return f'{self.yaml_header}\n\n{toc}\n\n{"\n\n----------\n\n".join(chunks)}'
