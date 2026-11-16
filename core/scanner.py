import os
from pathlib import Path
from core.file_info import FileInfo
from datetime import datetime

def scan(folders, extensions=None, min_size=0, max_size=None, modified_after=None, should_stop=None, on_file_scanned=None):
    if extensions is not None:
        extensions_set = set()
        for elem in extensions:
            extensions_set.add(elem.lower())

    def walk_through_folders(folder):
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    # Если пользователь нажал на "Остановить поиск" тут же выходим. Прокидываем данную функцию как аргумент функции scan(),
                    # так как scan() работает с каждым файлом, что позволяет моментально остановить поиск по нажатию
                    if should_stop is not None and should_stop():
                        return
                    if entry.name.startswith("."):
                        continue
                    path = entry.path
                    if entry.is_file(follow_symlinks=False):
                        if on_file_scanned is not None:
                            on_file_scanned()
                        if extensions is not None and Path(path).suffix.lower() not in extensions_set:
                            continue

                        try:
                            st = entry.stat()
                        except OSError:
                            continue

                        if st.st_size < min_size:
                            continue
                        if max_size is not None and st.st_size > max_size:
                            continue
                        if modified_after is not None and st.st_mtime < modified_after:
                            continue

                        yield FileInfo(path, st.st_size, st.st_mtime)

                    elif entry.is_dir(follow_symlinks=False):
                        yield from walk_through_folders(path)
        except OSError:
            return

    for folder in folders:
        if should_stop is not None and should_stop():
            return
        yield from walk_through_folders(folder)

# Тесты функции scan() на основе директории ~/Desktop/PythonProjects/scanner_test:
if __name__ == "__main__":
    TEST_DIR = Path.home() / "Desktop" / "PythonProjects" / "scanner_test"
    print("1. No filters")
    res = list(scan([TEST_DIR]))

    for elem in res:
        print(elem)
    print("Found at all:", len(res))

    print()

    print("2. Extensions filter .pdf")
    res = list(scan([TEST_DIR], extensions=[".pdf"]))

    for elem in res:
        print(elem)
    print("Found at all:", len(res))

    print()

    print("3. Extensions filter .PDF")
    res = list(scan([TEST_DIR], extensions=[".PDF"]))

    for elem in res:
        print(elem)
    print("Found at all:", len(res))

    print()

    print("4. Min_size and max_size filters")
    size = (TEST_DIR / "report.pdf").stat().st_size
    res = list(scan([TEST_DIR], min_size=size, max_size=size))

    for elem in res:
        print(elem)
    print("Found at all:", len(res))

    print()

    print("5. Modified_after filter")
    res = list(scan([TEST_DIR], modified_after=datetime(2025, 1, 1).timestamp()))

    for elem in res:
        print(elem)
    print("Found at all:", len(res))

    print()

    print("6. Two folders find in")
    res = list(scan([TEST_DIR / "Work", TEST_DIR / "Empty"]))

    for elem in res:
        print(elem)
    print("Found at all:", len(res))