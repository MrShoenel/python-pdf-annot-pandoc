from colorama import Fore, Style
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime



@dataclass
class Annotation:
    page: int
    author: str
    timestamp: datetime
    comment: str


@dataclass
class ProcessedPdf:
    pdf_file: Path
    annotations: list[Annotation]
    text: str=None

    @property
    def has_annotations(self) -> bool:
        return len(self.annotations) > 0

    @property
    def title(self) -> str:
        return self.pdf_file.stem
    
    def __hash__(self) -> int:
        return self.pdf_file.__hash__() ^ ('' if self.text is None else self.text).__hash__()
    

def print_red(s1: str, s2: str) -> None:
    print(f'{s1}{Fore.RED}{s2}{Style.RESET_ALL}')

def print_green(s1: str, s2: str) -> None:
    print(f'{s1}{Fore.GREEN}{s2}{Style.RESET_ALL}')

def print_yellow(s1: str, s2: str) -> None:
    print(f'{s1}{Fore.YELLOW}{s2}{Style.RESET_ALL}')


