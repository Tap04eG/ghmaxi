from core.input_recorder import InputRecorder
from core.input_player import InputPlayer

class TASEngine:
    def __init__(self):
        self.recorder = InputRecorder()
        self.player = InputPlayer()

    def run(self):
        print("TAS Engine запущен!")
        print("Команды:")
        print("  r - начать запись")
        print("  l <файл> - загрузить запись")
        print("  p - воспроизвести загруженную запись")
        print("  q - выход")
        print("\nГорячие клавиши во время записи:")
        print("  F9 - остановить запись и сохранить")

        
        while True:
            cmd = input("\nВведите команду: ").lower().strip()
            
            if cmd == "r":
                self.recorder.start_recording()
            elif cmd.startswith("l "):
                filename = cmd[2:].strip()
                self.player.load_recording(filename)
            elif cmd == "p":
                self.player.play_recording()
            elif cmd == "q":
                if self.recorder.is_recording:
                    self.recorder.stop_recording()
                if self.player.is_playing:
                    self.player.stop_recording()
                break
            else:
                print("Неизвестная команда")