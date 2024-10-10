import struct
import re

def read_png_chunks(file_path):
    chunks = []
    with open(file_path, 'rb') as f:
        if f.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")
        while True:
            try:
                length = struct.unpack('>I', f.read(4))[0]
                chunk_type = f.read(4)
                data = f.read(length)
                f.seek(4, 1)  # Skip CRC
                chunks.append((chunk_type, data))
                if chunk_type == b'IEND':
                    break
            except struct.error:
                break
    return chunks

def extract_stable_diffusion_metadata(file_path):
    chunks = read_png_chunks(file_path)
    for chunk_type, data in chunks:
        if chunk_type == b'tEXt':
            try:
                key, value = data.split(b'\0', 1)
                if key == b'parameters':
                    return value.decode('utf-8', errors='replace')
            except:
                pass
    return None

def format_metadata(metadata):
    parts = metadata.split("Negative prompt:", 1)
    
    if len(parts) > 1:
        prompt = parts[0].strip()
        rest = "Negative prompt:" + parts[1]
    else:
        match = re.search(r'\b\w+:', metadata)
        if match:
            split_index = match.start()
            prompt = metadata[:split_index].strip()
            rest = metadata[split_index:]
        else:
            prompt = metadata.strip()
            rest = ""
    
    formatted_rest = re.sub(r'([^,\s]+):', r'\n\1:', rest)
    return prompt, formatted_rest.strip()
