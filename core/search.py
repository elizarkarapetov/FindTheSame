from core.file_info import FileInfo
from core.scanner import scan
from core.hasher import hash_full
from core.hasher import hash_partial
import os
from pathlib import Path

# Функция поиска 100% копии эталона:
def find_exact(reference_path, folders, extensions=None, modified_after=None, should_stop=None, on_file_scanned=None):
    st = os.stat(reference_path)
    size = st.st_size
    mtime = st.st_mtime
    # Если эталон пустой - проверку делать нет смысла, смысловой нагрузки 0.
    if size == 0:
        return

    reference = FileInfo(reference_path, size, mtime)
    reference_hash_partial = hash_partial(reference.path, size)
    # Изначально полный хэш эталона не считаем, так как может быть ситуация, когда нет кандидатов, которые прошли хотя бы проверку на частичный хэш
    # Если таких нет, то и не нужно считать полный хэш эталона, так как файлы не прошли предыдущие проверки.
    reference_hash_full = None

    for candidate in scan(folders, extensions=extensions, min_size=size, max_size=size, modified_after=modified_after, should_stop=should_stop, on_file_scanned=on_file_scanned):
        if candidate == reference:
            continue

        try:
            candidate_hash_partial = hash_partial(candidate.path, candidate.size)
        except OSError:
            continue

        if candidate_hash_partial != reference_hash_partial:
            continue

        if reference_hash_full is None:
            reference_hash_full = hash_full(reference.path)

        try:
            candidate_hash_full = hash_full(candidate.path)
        except OSError:
            continue

        if candidate_hash_full != reference_hash_full:
            continue

        yield candidate

# Тесты функции find_exact() на основе директории ~/Desktop/PythonProjects/scanner_test:
if __name__ == "__main__":
    TEST_DIR = Path.home() / "Desktop" / "PythonProjects" / "scanner_test"
    print("1. Тест по папке scanner_test с эталоном report.pdf без фильтров")
    res = list(find_exact(TEST_DIR / "report.pdf", [TEST_DIR]))

    for file in res:
        print(file)

    print(f"Количество найденных полных копий: {len(res)}")

    print()

    print("2. Тест по папке scanner_test с эталоном report.pdf с фильтром на расширения .pdf")
    res1 = list(find_exact(TEST_DIR / "report.pdf", [TEST_DIR], extensions=[".pdf"]))

    for file in res1:
        print(file)

    print(f"Количество найденных полных копий: {len(res1)}")

    print()

    print("3. Тест по папке scanner_test с эталоном big1.bin без фильтров")
    res2 = list(find_exact(TEST_DIR / "big1.bin", [TEST_DIR]))

    for file in res2:
        print(file)

    print(f"Количество найденных полных копий: {len(res2)}")

    print()

    print("4. Тест по папке scanner_test с эталоном empty.txt (пустой файл) без фильтров")
    res3 = list(find_exact(TEST_DIR / "empty.txt", [TEST_DIR]))

    for file in res3:
        print(file)

    print(f"Количество найденных полных копий: {len(res3)}")