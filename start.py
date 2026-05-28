import os
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("как юзать:")
        print("  dev log     — включить запись")
        print("  dev replay  — отмотать время назад")
        print("  dev history — глянуть ленту изменений")
        return

    cmd = sys.argv[1]
    tool_dir = os.path.dirname(os.path.abspath(__file__))
    python_bin = os.path.join(tool_dir, "venv", "bin", "python")
    
    if not os.path.exists(python_bin):
        python_bin = sys.executable

    scripts = {
        "log": "dev_logger.py",
        "replay": "dev_player.py",
        "history": "dev_history.py"
    }

    if cmd in scripts:
        script_path = os.path.join(tool_dir, scripts[cmd])
        subprocess.call([python_bin, script_path])
    else:
        print(f"не знаю команду '{cmd}'. есть log, replay или history.")

if __name__ == "__main__":
    main()
