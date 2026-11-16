from PySide6.QtCore import QThread, Signal
from core.search import find_exact

# Шаг, с которым будет выводиться количество просмотренных файлов
PROGRESS_STEP = 100
# Класс рабочего потока - вынесем поиск копий в отдельный поток, который будет передавать сигналами главному потоку ошибки и найденные копии чтобы их отрисовать 
# в таблице найденных копий по мере нахождения. Нужно это для того, чтобы главное окно не зависало при поиске копий.
class SearchWorker(QThread):
    # Сигналы, первый будет отдаваться для отрисовки найденной копии, второй - для вызова окна ошибки (если будет проблема с прочтением эталона)
    copy_found = Signal(object)
    error = Signal(str)
    # Сигнал, который будет отдаваться для строки состояния внизу, чтобы показать сколько файлов уже просмотрено в ходе проверки
    progress = Signal(int)

    def __init__(self, reference, folders, extensions, modified_after):
        super().__init__()
        self.reference_path = reference
        self.folders_to_find = folders
        # Флаг нужен для того, чтобы отследить, не прерван ли поиск пользователем по нажатию кнопки "Остановить поиск"
        # Флаг позволяет вывести "Поиск прерван"
        self.was_stopped = False
        # Флаг нужен для того, чтобы отследить невыполнение поиска из-за ошибки чтения эталона
        # Необходим чтобы разделить случаи: произошла ошибка, или программа завершилась с корректным результатом
        self.failed = False
        # Количество просканированных файлов. Нужно для строки состояния
        self.scanned_count = 0

        # Введенные пользователем расширения и установленная им дата изменения файлов
        self.extensions = extensions
        self.modified_after = modified_after

    def run(self):
        try:
            for copy in find_exact(self.reference_path, self.folders_to_find, should_stop=self.isInterruptionRequested, on_file_scanned=self._on_file_scanned, extensions=self.extensions, modified_after=self.modified_after):
                # Сообщаем окну сигналом, что найдена копия
                self.copy_found.emit(copy)
            # Проверяем, не нажал ли пользователь кнопку "Остановить поиск"
            if self.isInterruptionRequested():
                self.was_stopped = True
        except OSError as e:
            # Сообщаем окну сигналом, что произошла ошибка чтения эталона
            self.failed = True
            self.error.emit(str(e))

    # Метод, вызывающийся сканером (scan()) на каждом файле, а сигнал отправляется только каждый 100-ый файл, чтобы не перегрузить главный поток
    def _on_file_scanned(self):
        self.scanned_count += 1
        if self.scanned_count % PROGRESS_STEP == 0:
            self.progress.emit(self.scanned_count)