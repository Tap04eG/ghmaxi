import time
import os
import json
import datetime
from pynput import keyboard

class InputRecorder:
    def __init__(self):
        self.is_recording = False
        self.actions = []
        self._t0 = None
        self._listener = None
        self._pressed = set()

    def start_recording(self):
        if self.is_recording:
            return
        
        self.actions = []
        self._t0 = time.perf_counter()
        self._pressed = set()
        
        self._listener = keyboard.Listener(
            on_press=self._on_press, 
            on_release=self._on_release
            )

        self._listener.start()
        self.is_recording = True
        print("Запись началась")

    def stop_recording(self):
        if not self.is_recording:
            return
        
        if self._listener:
            self._listener.stop()
            self._listener = None
        
        self.is_recording = False
        print(f"Запись остановлена. Событий: {len(self.actions)}")
        
        # Очищаем состояние
        self._pressed.clear()
        
        # Автоматически сохраняем при остановке
        if self.actions:
            self.save_recording()
    
    def force_stop(self):
        """Принудительная остановка записи без сохранения"""
        if self._listener:
            self._listener.stop()
            self._listener = None
        
        self.is_recording = False
        self._pressed.clear()
        self.actions.clear()
        print("Запись принудительно остановлена")

    def save_recording(self, filename=None):
        if not self.actions:
            print("Нет событий для сохранения!")
            return None
        
        os.makedirs("recordings", exist_ok=True)
        
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.jsonl"
        
        filepath = os.path.join("recordings", filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for event in self.actions:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
            
            print(f"Запись сохранена: {filepath}")
            return filepath
        except Exception as e:
            print(f"Ошибка сохранения записи: {e}")
            return None

    def _on_press(self, key):
        if not self.is_recording or self._t0 is None:
            return
        
        # Проверяем на нажатие F9
        if key == keyboard.Key.f9:
            print("\n[F9] Остановка записи...")
            self.stop_recording()
            return
        
        try:
            # Получаем имя клавиши
            if key.char is not None and key.char:
                # Обычные символы пишем как есть
                key_name = key.char
            else:
                # специальные через Key.*
                key_name = str(key)
        except AttributeError:
            key_name = str(key)
        
        # Проверяем, что имя клавиши не пустое
        if not key_name or key_name.strip() == "":
            print(f"Пропущена пустая клавиша: {key}")
            return
        
        if key_name not in self._pressed:
            self._pressed.add(key_name)
            try:
                event = {
                    "t": time.perf_counter() - self._t0,
                    "type": "press",
                    "key": key_name
                }
                self.actions.append(event)
                print(f"Нажата: {key_name}")
            except Exception as e:
                print(f"Ошибка записи нажатия {key_name}: {e}")
                self._pressed.discard(key_name)  # Убираем из множества при ошибке

    def _on_release(self, key):
        if not self.is_recording or self._t0 is None:
            return
        
        try:
            if key.char is not None and key.char:
                key_name = key.char
            else:
                key_name = str(key)
        except AttributeError:
            key_name = str(key)
        
        if not key_name or key_name.strip() == "":
            print(f"Пропущена пустая клавиша: {key}")
            return
        
        if key_name in self._pressed:
            self._pressed.remove(key_name)
            try:
                event = {
                    "t": time.perf_counter() - self._t0,
                    "type": "release",
                    "key": key_name
                }
                self.actions.append(event)
                print(f"Отпущена: {key_name}")
            except Exception as e:
                print(f"Ошибка записи отпускания {key_name}: {e}")
                # Возвращаем клавишу в множество при ошибке
                self._pressed.add(key_name)