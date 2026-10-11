import re


class DocumentProcessor:
    def process(self, content: str) -> str:
        if not isinstance(content, str):
            raise TypeError("Document content must be a string")

        # Normalize line endings and remove unnecessary spaces.
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # Normalize repeated spaces and tabs.
        content = re.sub(r"[ \t]+", " ", content)

        # Remove spaces adjacent to line breaks.
        content = re.sub(r" *\n *", "\n", content)

        # Limit consecutive blank lines to a single blank line.
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Remove leading and trailing whitespace.
        return content.strip()
