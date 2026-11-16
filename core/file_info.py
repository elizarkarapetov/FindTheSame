from pathlib import Path

class FileInfo:
    def __init__(self, path, size, mtime):
        self.path = Path(path).resolve()
        self.size = size
        self.mtime = mtime
        self.extension = (self.path.suffix).lower()

    def __repr__(self):
        return f"FileInfo(path={self.path}, size={self.size}, mtime={self.mtime})"

    def __eq__(self, other):
        if not isinstance(other, FileInfo):
            return NotImplemented

        return self.path == other.path