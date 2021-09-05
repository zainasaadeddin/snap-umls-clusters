from typing import List
import re
import PyPDF2

from . import Types


def load_sentences_from_pdf(filepath: str) -> List[Types.Sentence]:
    """

    Reads a .pdf file and loads contained questions
    by using regex patterns on its text content.

    """
    sentence_pattern = r"\d+\.* [^_]+"
    number_pattern = r"^(\d+)[\. ]*"

    with open(filepath, 'rb') as f:
        content = PyPDF2.PdfFileReader(f)
        content = "\n".join([
            page.extractText()
            for page in content.pages
        ])
        sentences = re.findall(sentence_pattern, content)

    allowed_sentences = []
    expected_index = 1
    for sentence in sentences:
        Ok = False
        number = re.findall(number_pattern, sentence)
        if number:
            n = int(number[0])
            if n == expected_index:
                Ok = True
                expected_index += 1

        if not Ok:
            break
        text = re.sub(number_pattern, "", sentence)

        # Quotes might be read as bugged characters... remove them.
        text = re.sub("[ﬁﬂ]+", "", text)

        assert text
        # output = re.sub(r"\d+\. ", "", sentence)
        allowed_sentences.append(Types.Sentence(n, text))

    return allowed_sentences
