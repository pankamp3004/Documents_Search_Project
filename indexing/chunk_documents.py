CHUNK_SIZE = 400
OVERLAP = 80

def chunk_text(text):
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk_words = words[i:i+CHUNK_SIZE]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)
        i += CHUNK_SIZE - OVERLAP

    return chunks
