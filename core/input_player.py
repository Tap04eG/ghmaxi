import time
import json
import os
from pynput import keyboard

class InputPlayer:
    def __init__(self):
        self.is_playing = False
        self.loaded_actions = []
        self._controller = None
        self._playback_thread = None

    def load_recording(self, filename):
        if not os.path.exists(filename):
            print(f"Файл не найден: {filename}")
            return False
        
        try:
            self.loaded_actions = []
            with open(filename, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # Пропускаем пустые строки
                        continue
                    try:
                        event = json.loads(line)
                        self.loaded_actions.append(event)
                    except json.JSONDecodeError as e:
                        print(f"Ошибка в строке {line_num}: {e}")
                        continue
            
            print(f"Загружено {len(self.loaded_actions)} событий")
            return True
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            self.loaded_actions = []
            return False

    def play_recording(self):
        if not self.loaded_actions:
            print("Нет загруженных действий!")
            return
        
        if self.is_playing:
            print("Уже воспроизводится!")
            return
        
        self.is_playing = True
        self._controller = keyboard.Controller()
        print("Начинаем воспроизведение...")
        
        # Воспроизведение с правильными таймингами
        last_time = 0
        for event in self.loaded_actions:
            if not self.is_playing:
                break
            
            # Ждём интервал между событиями
            sleep_time = event["t"] - last_time
            if sleep_time > 0:
                time.sleep(sleep_time)
            elif sleep_time < 0:
                print(f"Предупреждение: отрицательное время {sleep_time:.6f}s")
            
            try:
                if event["type"] == "press":
                    key_obj = self._string_to_key(event["key"])
                    self._controller.press(key_obj)
                elif event["type"] == "release":
                    key_obj = self._string_to_key(event["key"])
                    self._controller.release(key_obj)
            except Exception as e:
                print(f"Ошибка воспроизведения: {e}")
            
            last_time = event["t"]
        
        self.is_playing = False
        print("Воспроизведение завершено")

    # def pause_recording(self):
    #     self.is_playing = False
    #     print("Воспроизведение приостановлено")

    # def stop_recording(self):
    #     self.is_playing = False
    #     print("Воспроизведение остановлено")

    def _string_to_key(self, key_string):
        """Преобразует строку обратно в объект клавиши"""
        try:
            if key_string.startswith("Key."):
                key_name = key_string[4:]  # убираем "Key."
                return getattr(keyboard.Key, key_name)
            else:
                # pynput автоматически определит раскладку
                return key_string
        except AttributeError:
            # Если не можем найти клавишу, возвращаем как есть
            print(f"Неизвестная клавиша: {key_string}")
            return key_string