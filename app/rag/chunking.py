class TextChunker:

    def __init__(
        self,
        chunk_size=1000,
        chunk_overlap=150,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text):
        clean_text = " ".join(text.split())

        if not clean_text:
            return []

        chunks = []
        start = 0
        text_length = len(clean_text)

        while start < text_length:
            end = min(
                start + self.chunk_size,
                text_length,
            )

            chunk = clean_text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            start = end - self.chunk_overlap

        return chunks