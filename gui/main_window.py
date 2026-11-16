from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QMainWindow, QLineEdit, QFileDialog, QListWidget, QAbstractItemView, QTableWidget, QMessageBox, QTableWidgetItem, QGroupBox, QCheckBox, QDateEdit, QApplication, QHeaderView
from PySide6.QtCore import QDate, Qt, QUrl, QFile
from PySide6.QtGui import QDesktopServices
from pathlib import Path
from datetime import datetime
import sys
import subprocess
from gui.worker import SearchWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FindTheSame - поиск файлов с одинаковым содержимым")
        self.resize(900, 600)
        self._build_ui()
        self._connect_signals()
        self.worker = None
        self.setAcceptDrops(True)

    # Метод, создающий виджеты и раскладки
    def _build_ui(self):
        self.label_reference = QLabel("Эталон (файл):")
        self.line_reference_path = QLineEdit()
        self.line_reference_path.setReadOnly(True)
        self.button_choose_reference = QPushButton("Выбрать...")

        reference_layout = QHBoxLayout()
        reference_layout.addWidget(self.label_reference)
        reference_layout.addWidget(self.line_reference_path)
        reference_layout.addWidget(self.button_choose_reference)

        self.label_folders_to_find_in = QLabel("Папки для поиска:")
        self.list_of_folders = QListWidget()
        self.list_of_folders.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_of_folders.setMaximumHeight(100)
        self.button_add_folder = QPushButton("Добавить...")
        self.button_delete_folder = QPushButton("Удалить")

        buttons_add_delete_layout = QVBoxLayout()
        buttons_add_delete_layout.addWidget(self.button_add_folder)
        buttons_add_delete_layout.addWidget(self.button_delete_folder)
        buttons_add_delete_layout.addStretch()

        list_and_buttons_layout = QHBoxLayout()
        list_and_buttons_layout.addWidget(self.list_of_folders)
        list_and_buttons_layout.addLayout(buttons_add_delete_layout)

        self.button_find = QPushButton("Найти")
        self.button_stop_finding = QPushButton("Остановить поиск")
        # Кнопка "Остановить поиск" до начала поиска недоступна
        self.button_stop_finding.setEnabled(False)
        self.label_results = QLabel("Результаты:")
        self.table_results = QTableWidget(0, 4)
        self.table_results.setHorizontalHeaderLabels(["Имя", "Папка", "Размер", "Изменён"])
        self.table_results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_results.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.table_results.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        button_find_stop_layout = QHBoxLayout()
        button_find_stop_layout.addStretch()
        button_find_stop_layout.addWidget(self.button_find)
        button_find_stop_layout.addWidget(self.button_stop_finding)

        self.filters_box = QGroupBox("Фильтры поиска")
        self.label_types_of_files = QLabel("Типы файлов:")
        self.line_extensions = QLineEdit()
        self.line_extensions.setPlaceholderText("например: pdf, docx, doc (если пусто - значит все типы)")
        self.check_box_mtime = QCheckBox("Изменён после:")
        self.date_modified_after = QDateEdit()
        self.date_modified_after.setDate(QDate.currentDate())
        self.date_modified_after.setCalendarPopup(True)
        self.date_modified_after.setEnabled(False)

        types_and_extensions_layout = QHBoxLayout()
        types_and_extensions_layout.addWidget(self.label_types_of_files)
        types_and_extensions_layout.addWidget(self.line_extensions)

        check_box_and_date_layout = QHBoxLayout()
        check_box_and_date_layout.addWidget(self.check_box_mtime)
        check_box_and_date_layout.addWidget(self.date_modified_after)
        check_box_and_date_layout.addStretch()

        extensions_and_mtime_layout = QVBoxLayout()
        extensions_and_mtime_layout.addLayout(types_and_extensions_layout)
        extensions_and_mtime_layout.addLayout(check_box_and_date_layout)

        self.filters_box.setLayout(extensions_and_mtime_layout)

        self.button_open_file = QPushButton("Открыть")
        self.button_open_file.setEnabled(False)
        self.button_show_in_finder = QPushButton("Показать в Finder/Проводнике")
        self.button_show_in_finder.setEnabled(False)
        self.button_copy_path = QPushButton("Скопировать путь")
        self.button_copy_path.setEnabled(False)
        self.button_move_to_trash = QPushButton("Переместить в Корзину")
        self.button_move_to_trash.setEnabled(False)

        buttons_to_interact_with_results = QHBoxLayout()
        buttons_to_interact_with_results.addWidget(self.button_open_file)
        buttons_to_interact_with_results.addWidget(self.button_show_in_finder)
        buttons_to_interact_with_results.addWidget(self.button_copy_path)
        buttons_to_interact_with_results.addStretch()
        buttons_to_interact_with_results.addWidget(self.button_move_to_trash)

        main_layout = QVBoxLayout()
        main_layout.addLayout(reference_layout)
        main_layout.addWidget(self.label_folders_to_find_in)
        main_layout.addLayout(list_and_buttons_layout)
        main_layout.addWidget(self.filters_box)
        main_layout.addLayout(button_find_stop_layout)
        main_layout.addWidget(self.label_results)
        main_layout.addWidget(self.table_results, 1)
        main_layout.addLayout(buttons_to_interact_with_results)

        central_part = QWidget()
        central_part.setLayout(main_layout)
        self.setCentralWidget(central_part)

    # Метод, "оживляющий" кнопки, привязывающий функции к кнопкам
    def _connect_signals(self):
        self.button_choose_reference.clicked.connect(self.on_click_choose_reference)
        self.button_add_folder.clicked.connect(self.on_click_add_folder)
        self.button_delete_folder.clicked.connect(self.on_click_delete_folder)
        self.button_find.clicked.connect(self.on_click_find)
        self.button_stop_finding.clicked.connect(self.on_click_stop)
        self.check_box_mtime.toggled.connect(self.date_modified_after.setEnabled)
        self.table_results.itemSelectionChanged.connect(self._update_buttons_after_selection_results)
        self.table_results.cellDoubleClicked.connect(self.on_double_click_result)
        self.button_open_file.clicked.connect(self.on_click_open_file)
        self.button_show_in_finder.clicked.connect(self.on_click_show_in_folder)
        self.button_copy_path.clicked.connect(self.on_click_copy_path)
        self.button_move_to_trash.clicked.connect(self.on_click_move_to_trash)

    # Метод для разбора введенных пользователем расширений в качестве фильтра поиска. Результат данного метода уходит в рабочий поток
    def _parse_extensions(self, text):
        extensions = text.replace(",", " ").replace(";", " ").replace("|", " ").replace("/", " ").split()
        valid_extensions = []
        invalid_extensions = []

        for elem in extensions:
            elem = elem.strip("*.")
            if elem == "":
                continue
            if elem.isalnum():
                valid_extensions.append("." + elem)
                continue
            invalid_extensions.append(elem)

        if not valid_extensions:
            return None, invalid_extensions

        return valid_extensions, invalid_extensions

    # Метод, результат которого - значение поля "изменён после". Результат данного метода уходит в рабочий поток
    def _modified_after(self):
        modified_after = None
        chosen_date = self.date_modified_after.date()
        if self.check_box_mtime.isChecked():
            modified_after = datetime(chosen_date.year(), chosen_date.month(), chosen_date.day()).timestamp()

        return modified_after

    # Метод для получения путей к выделенным результатам (найденным копиям заданного файла) из таблицы результатов
    def _selected_paths(self):
        paths_of_selected_results = []

        # Проходимся по координатам выделенных результатов в таблице результатов
        for index in self.table_results.selectionModel().selectedRows():
            # Берем путь, обращаясь к координате по .row(), чтобы получить номер ряда (строки) в таблице результатов, и 0 - фиксированно, так как мы положили
            # путь как скрытый текст в столбец с именем файла копии, а этот столбец нулевой
            path = Path(self.table_results.item(index.row(), 0).data(Qt.ItemDataRole.UserRole))
            paths_of_selected_results.append(path)

        return paths_of_selected_results

    # Метод, для включения/выключения кнопок под таблицей результатов в соответствии с количеством выделенных пользователем результатов
    def _update_buttons_after_selection_results(self):
        selected_results_num = len(self._selected_paths())

        self.button_open_file.setEnabled(selected_results_num == 1)
        self.button_show_in_finder.setEnabled(selected_results_num == 1)
        self.button_copy_path.setEnabled(selected_results_num == 1)
        self.button_move_to_trash.setEnabled(selected_results_num >= 1)

    # Общий метод-обертка над функцией открытия файла (по даблклику или по кнопке "Открыть")
    def _open_file(self, path):
        if not path.is_file():
            QMessageBox.critical(self, "Ошибка при попытке открыть выбранный файл", f"Выбранный файл не найден: {path}. Возможно, он был перемещён или удалён после поиска.")
            return

        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            QMessageBox.warning(self, "Ошибка", "Не удалось открыть файл: нет программы для файлов этого типа")

    # Общий метод добавления папки для поиска, для двух случаев: добавление по кнопке "Добавить..." и добавление перетаскиванием
    def _add_folder(self, folder):
        relative_folders_to_delete = []

        for i in range(self.list_of_folders.count()):
            if Path(folder).is_relative_to(Path(self.list_of_folders.item(i).text())):
                self.statusBar().showMessage("⚠️ Выбранная папка входит в уже добавленную папку", 5000)
                return False
            if Path(self.list_of_folders.item(i).text()).is_relative_to(Path(folder)):
                relative_folders_to_delete.append(self.list_of_folders.item(i))

        for relative in relative_folders_to_delete:
            self.list_of_folders.takeItem(self.list_of_folders.row(relative))

        self.list_of_folders.addItem(folder)

        if relative_folders_to_delete != []:
            self.statusBar().showMessage(f"✅ Выбранная папка добавлена, вложенных в нее папок удалено: {len(relative_folders_to_delete)}", 5000)
        return True

    # Вспомогательный метод для отображения размеров файлов в итоговой таблице в удобном формате.
    def _format_size(self, size):
        units = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
        index = 0

        result_size = size
        while result_size >= 1024 and index != len(units) - 1:
            result_size = result_size / 1024
            index += 1

        if index == 0:
            return f"{result_size} {units[0]}"

        return f"{result_size:.2f} {units[index]}".replace(".", ",")

    # Переопределение стандартного обработчика события закрытия окна, чтобы при закрытии программы во время ее работы (поиска копий)
    # завершение не было аварийным (программу закрыли, а поток еще работает)
    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait()

        super().closeEvent(event)

    # Переопределение стандартного обработчика события перетаскивания файла/папки в окно. Если идет поиск - перетащить нельзя,
    # Если файл или папка и поиск не идет - перетащить можно, если поиск не идет и это не файл/папка - перетащить нельзя.
    def dragEnterEvent(self, event):
        if (self.worker is not None) and (self.worker.isRunning()):
            event.ignore()
            return
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            return

        event.ignore()

    # Переопределение метода бросания объектов в окно. Если папка - кладем в папки для поиска, если файл - кладем в эталон.
    def dropEvent(self, event):
        objs = event.mimeData().urls()
        got_reference_path = False
        count_dirs = 0
        declined_dirs = 0
        declined_files = 0

        for obj in objs:
            if not obj.isLocalFile():
                continue

            obj_path = Path(obj.toLocalFile())
            if obj_path.is_dir():
                if self._add_folder(str(obj_path)):
                    count_dirs += 1
                else:
                    declined_dirs += 1

            elif obj_path.is_file():
                if got_reference_path:
                    declined_files += 1
                    continue
                got_reference_path = True
                self.line_reference_path.setText(str(obj_path))

        # Соберем итоговое сообщение в строке состояния только из тех частей, которые не равны 0. То есть не будем показывать пользователю, что
        # Папок добавлено: 0, то есть выводим фразы только со смысловой нагрузкой.
        final_message = []

        if got_reference_path:
            final_message.append("✅ Эталон установлен")
        if count_dirs > 0:
            final_message.append(f"Папок добавлено: {count_dirs}")
        if declined_dirs > 0:
            final_message.append(f"Папок пропущено: {declined_dirs}")
        if declined_files > 0:
            final_message.append(f"Файлов пропущено: {declined_files}")

        text = ", ".join(final_message)

        if final_message == []:
            self.statusBar().showMessage("⚠️ Ничего не добавлено: можно перетаскивать только файлы и папки с компьютера", 5000)
        else:
            self.statusBar().showMessage(text, 5000)

        event.acceptProposedAction()

    # Метод для выбора эталонного файла
    def on_click_choose_reference(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите эталонный файл")

        if path == "":
            return

        self.line_reference_path.setText(path)

    # Метод для выбора папок для поиска (добавление папок по одной за раз)
    def on_click_add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для поиска")

        if folder == "":
            return

        self._add_folder(folder)

    # Метод для удаления выбранных папок для поиска (можно удалить несколько сразу)
    def on_click_delete_folder(self):
        folders_to_delete = self.list_of_folders.selectedItems()

        if folders_to_delete == []:
            return

        for folder in folders_to_delete:
            self.list_of_folders.takeItem(self.list_of_folders.row(folder))

    # Метод для поиска копий эталона
    def on_click_find(self):
        if self.line_reference_path.text() == "":
            QMessageBox.warning(self, "Эталон не выбран", "Сначала выберите эталонный файл")
            return

        folders_to_find_in = [self.list_of_folders.item(i).text() for i in range(self.list_of_folders.count())]

        if folders_to_find_in == []:
            QMessageBox.warning(self, "Папки для поиска копий не выбраны", "Необходимо выбрать папки для поиска копий")
            return

        try:
            if Path(self.line_reference_path.text()).stat().st_size == 0:
                QMessageBox.information(self, "Файл эталона пустой", "Эталон - пустой файл (0 байт), искать его копии не имеет смысла")
                return
        except OSError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать эталон: {e}")
            return

        valid_extensions, invalid_extensions = self._parse_extensions(self.line_extensions.text())
        modified_after = self._modified_after()

        if invalid_extensions:
            str_invalid_extensions = ", ".join(invalid_extensions)
            QMessageBox.warning(self, "Ошибка распознавания типов файлов", f"Не удалось распознать типы файлов: {str_invalid_extensions}. Укажите расширения через запятую или пробел, например: pdf, docx, doc")
            return

        self.table_results.setRowCount(0)
        self._update_buttons_after_selection_results()
        
        self.worker = SearchWorker(self.line_reference_path.text(), folders_to_find_in, valid_extensions, modified_after)
        self.button_find.setEnabled(False)
        self.button_choose_reference.setEnabled(False)
        self.button_add_folder.setEnabled(False)
        self.button_delete_folder.setEnabled(False)
        self.button_stop_finding.setEnabled(True)
        self.filters_box.setEnabled(False)

        self.worker.copy_found.connect(self.on_copy_found)
        self.worker.error.connect(self.on_search_error)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.progress.connect(self.on_scanned_files)
        self.worker.start()

        self.statusBar().showMessage("Идет поиск...")

    # Метод для отрисовки каждой найденной копии. Этот метод вызывается по сигналу рабочего потока
    def on_copy_found(self, copy):
        row = self.table_results.rowCount()
        self.table_results.insertRow(row)
        # Кладем путь как невидимый текст в строку с результатом в 0-ой столбец, там где имя файла найденной копии
        item = QTableWidgetItem(copy.path.name)
        item.setData(Qt.ItemDataRole.UserRole, str(copy.path))
        self.table_results.setItem(row, 0, item)
        self.table_results.setItem(row, 1, QTableWidgetItem(str(copy.path.parent)))
        self.table_results.setItem(row, 2, QTableWidgetItem(self._format_size(copy.size)))
        self.table_results.setItem(row, 3, QTableWidgetItem(datetime.fromtimestamp(copy.mtime).strftime("%d.%m.%Y %H:%M")))

    # Метод для объявления ошибки прочтения эталона. Метод вызывается по сигналу рабочего потока
    def on_search_error(self, error_text):
        QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать эталон: {error_text}")

    # Метод, вызываемый сигналом от рабочего потока, когда он закончил свою работу
    def on_search_finished(self):
        self.button_find.setEnabled(True)
        self.button_choose_reference.setEnabled(True)
        self.button_add_folder.setEnabled(True)
        self.button_delete_folder.setEnabled(True)
        self.button_stop_finding.setEnabled(False)
        self.filters_box.setEnabled(True)

        if self.worker.failed:
            self.statusBar().showMessage("❌ Поиск не выполнен")
            return
        
        if self.worker.was_stopped:
            self.statusBar().showMessage(f"⚠️ Поиск прерван, просмотрено файлов - {self.worker.scanned_count}, найдено копий - {self.table_results.rowCount()}")
            return

        self.statusBar().showMessage(f"✅ Поиск успешно выполнен, просмотрено файлов - {self.worker.scanned_count}, найдено копий - {self.table_results.rowCount()}")

    # Метод для корректной остановки поиска (мы бросаем рабочему потоку запрос на остановку, а тот проверяет есть ли такой запрос абсолютно для каждого вхождения в папку)
    # Срабатывает по нажатию на кнопку "Остановить поиск"
    def on_click_stop(self):
        self.button_stop_finding.setEnabled(False)
        self.worker.requestInterruption()
        self.statusBar().showMessage("Остановка поиска...")

    # Метод, вызываемый сигналом от рабочего потока во время его основной работы, чтобы подтягивать количество просмотренных файлов в строке состояния
    def on_scanned_files(self, scanned_count):
        self.statusBar().showMessage(f"Идет поиск... просмотрено файлов: {scanned_count}")

    # Метод, вызывающий общий метод открытия файла (по нажатию на отдельную кнопку "Открыть" или по двойному клику на результат в таблице результатов)
    # Данный метод для случая, когда нажали отдельную кнопку "Открыть"
    def on_click_open_file(self):
        path = self._selected_paths()[0]

        self._open_file(path)

    # Метод, вызывающий общий метод открытия файла (по нажатию на отдельную кнопку "Открыть" или по двойному клику на результат в таблице результатов)
    # Данный метод для случая, когда нажали двойным нажатием на результат в таблице результатов
    def on_double_click_result(self, row, column):
        path = Path(self.table_results.item(row, 0).data(Qt.ItemDataRole.UserRole))

        self._open_file(path)

    # Метод, вызываемый нажатием на кнопку "Показать в Finder/Проводнике"
    def on_click_show_in_folder(self):
        path = self._selected_paths()[0]

        if not path.is_file():
            QMessageBox.critical(self, "Ошибка при попытке найти выбранный файл", f"Выбранный файл не найден: {path}. Возможно, он был перемещён или удалён после поиска.")
            return

        platform = sys.platform

        # Если платформа - Mac, показываем файл в Finder
        if platform == "darwin":
            subprocess.run(["open", "-R", str(path)])
        # Если платформа - Windows, показываем файл в проводнике
        elif platform == "win32":
            subprocess.run(["explorer", "/select,", str(path)])
        # Если платформа - любая другая, показываем файл в файловом менеджере, который настроен в системе, но без его выделения, просто открываем папку где он лежит
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))

    # Метод, вызываемый нажатием на кнопку "Скопировать путь"
    def on_click_copy_path(self):
        path = str(self._selected_paths()[0])

        QApplication.clipboard().setText(path)

        self.statusBar().showMessage("✅ Путь к выбранному файлу скопирован в буфер обмена", 5000)

    # Метод, вызываемый нажатием на кнопку "Переместить в Корзину". Перемещает все выделенные результаты
    def on_click_move_to_trash(self):
        selected_files_num = len(self._selected_paths())

        answer = QMessageBox.question(self, "Перемещение в Корзину", f"Переместить в Корзину выбранные файлы - {selected_files_num}?")

        if answer != QMessageBox.StandardButton.Yes:
            return

        rows_to_delete_from_table = []
        count_moved_to_trash = 0
        count_failed_to_move = 0
        for index in self.table_results.selectionModel().selectedRows():
            row_num = index.row()
            item = self.table_results.item(row_num, 0)
            path = Path(item.data(Qt.ItemDataRole.UserRole))

            if QFile.moveToTrash(str(path)):
                rows_to_delete_from_table.append(item)
                count_moved_to_trash += 1
                continue

            count_failed_to_move += 1

        for item in rows_to_delete_from_table:
            self.table_results.removeRow(self.table_results.row(item))

        self._update_buttons_after_selection_results()

        if count_failed_to_move > 0:
            self.statusBar().showMessage(f"✅ Перемещено в Корзину: {count_moved_to_trash}, ⚠️ Не удалось переместить: {count_failed_to_move}")
            return

        self.statusBar().showMessage(f"✅ Перемещено в Корзину: {count_moved_to_trash} (все выбранные файлы)")