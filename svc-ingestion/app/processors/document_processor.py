import re


class DocumentProcessor:
    def process(self, content: str) -> str:
        print(f"<< FILE RECEIVED IN document_processor.process: OK >>")
        if not isinstance(content, str):
            raise TypeError("Document content must be a string")

        # Normalize line endings and remove unnecessary spaces.
        print("<< NORMALIZING LINE-ENDINGS... >>")
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # Normalize repeated spaces and tabs.
        print("<< NORMALIZING BLANKS... >>")
        content = re.sub(r"[ \t]+", " ", content)

        # Remove spaces adjacent to line breaks.
        print("<< NORMALIZING LINE BREAKS... >>")
        content = re.sub(r" *\n *", "\n", content)

        # Limit consecutive blank lines to a single blank line.
        print("<< NORMALIZING LINES... >>")
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Remove leading and trailing whitespace.
        print("<< ALL NORMALIZING TASKS COMPLETED SUCCESSFULLY >>")
        return content.strip()
