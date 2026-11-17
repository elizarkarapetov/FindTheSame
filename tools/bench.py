# Замеры для раздела «Тестирование производительности» пояснительной записки.
# Повторяет каскад из find_exact, но считает, сколько файлов прошло каждую проверку.
# Запуск из корня проекта:
#   python -m tools.bench <эталон> <папка>            – каскадный поиск
#   python -m tools.bench <эталон> <папка> --naive    – плюс наивный поиск для сравнения
import sys
import time
from pathlib import Path
from core.scanner import scan
from core.hasher import hash_partial, hash_full

reference = Path(sys.argv[1]).expanduser().resolve()
folder = Path(sys.argv[2]).expanduser()
size = reference.stat().st_size

# Счётчик просмотренных файлов – передаётся в scan() так же, как в программе
scanned = 0
def count_file():
    global scanned
    scanned += 1

# Каскадный поиск: размер -> частичный хеш -> полный хеш
start = time.perf_counter()
ref_partial = hash_partial(reference, size)
ref_full = hash_full(reference)
same_size = 0
same_partial = 0
copies = 0
for file in scan([folder], min_size=size, max_size=size, on_file_scanned=count_file):
    if file.path == reference:
        continue
    same_size += 1
    try:
        if hash_partial(file.path, size) != ref_partial:
            continue
        same_partial += 1
        if hash_full(file.path) == ref_full:
            copies += 1
    except OSError:
        continue
cascade_time = time.perf_counter() - start

print(f"Эталон: {reference.name}, {size} байт")
print(f"Просмотрено файлов: {scanned}")
print(f"Совпал размер: {same_size}")
print(f"Совпал частичный хеш: {same_partial}")
print(f"Найдено копий: {copies}")
print(f"Время каскадного поиска: {cascade_time:.2f} с")

# Наивный поиск: полный хеш каждого файла без предварительных проверок
if "--naive" in sys.argv:
    start = time.perf_counter()
    naive_copies = 0
    read_bytes = 0
    for file in scan([folder]):
        if file.path == reference:
            continue
        try:
            if hash_full(file.path) == ref_full:
                naive_copies += 1
            read_bytes += file.size
        except OSError:
            continue
    naive_time = time.perf_counter() - start
    print(f"Наивный поиск: копий {naive_copies}, прочитано {read_bytes / 1024 / 1024:.1f} МБ, время {naive_time:.2f} с")