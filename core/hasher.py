import hashlib

# Блок фиксированного размера 1МБ скармливаем hasher'у, чтобы не забивать память всем файлом сразу:
BLOCK = 1024 * 1024

def hash_full(path):
    hasher = hashlib.sha256()

    with open(path, "rb") as file:
        while True:
            block = file.read(BLOCK)
            if block == b"":
                break
            hasher.update(block)

    return hasher.hexdigest()

# Для проверки начальной и конечной части файла, определим размер этой части 64КБ - это один из этапов каскада проверок файла:
PART = 64 * 1024

def hash_partial(path, size):
    if size > 2 * PART:
        hasher = hashlib.sha256()
        with open(path, "rb") as file:
            start = file.read(PART)
            file.seek(size - PART)
            end = file.read(PART)
            hasher.update(start+end)

    else:
        return hash_full(path)

    return hasher.hexdigest()