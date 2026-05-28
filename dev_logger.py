import os
import time
import json
import difflib
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.dev-replay', 'venv', 'env'}
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.txt'}

def get_clean_path():
    p = input("где проект? (Enter если тут): ").strip()
    if not p or p == '.': return os.getcwd()
    if p.startswith('home/'): p = '/' + p
    path = os.path.abspath(os.path.expanduser(p))
    if not os.path.exists(path):
        print(f"папку не нашел, буду следить тут: {os.getcwd()}")
        return os.getcwd()
    return path

class DevReplayHandler(FileSystemEventHandler):
    def __init__(self, base_path):
        self.base_path = base_path
        self.file_cache = {}
        self.last_event_time = {}
        self.replay_dir = os.path.join(self.base_path, '.dev-replay')
        self.log_file = os.path.join(self.replay_dir, 'log.jsonl')
        
        os.makedirs(self.replay_dir, exist_ok=True)
        self._preload_files()
        print(f"\nпогнали. слежу за: {self.base_path}")
        print("для выхода жми Ctrl+C\n")

    def _is_valid_file(self, path):
        parts = path.replace(self.base_path, '').split(os.sep)
        return not any(part in IGNORE_DIRS for part in parts) and os.path.splitext(path)[1] in ALLOWED_EXTENSIONS

    def _preload_files(self):
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                filepath = os.path.join(root, file)
                if self._is_valid_file(filepath):
                    self.file_cache[filepath] = self._read_file(filepath)

    def _read_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f: return f.readlines()
        except: return []

    def on_modified(self, event):
        if not event.is_directory: self._process_change(event.src_path)

    def _process_change(self, filepath):
        if not self._is_valid_file(filepath): return
        current_time = time.time()
        if filepath in self.last_event_time and (current_time - self.last_event_time[filepath] < 0.5): return
        self.last_event_time[filepath] = current_time

        new_content = self._read_file(filepath)
        old_content = self.file_cache.get(filepath, [])

        if new_content != old_content:
            diff = list(difflib.unified_diff(old_content, new_content, fromfile='old', tofile='new', n=0))
            if diff:
                actions = self._parse_to_human_readable(diff)
                if actions:
                    rel_path = os.path.relpath(filepath, self.base_path)
                    self._log_event(rel_path, actions, "".join(new_content))
                self.file_cache[filepath] = new_content

    def _parse_to_human_readable(self, diff_lines):
        actions = []
        current_line = 0
        for line in diff_lines:
            m = re.search(r'\+(\d+)', line)
            if line.startswith('@@') and m:
                current_line = int(m.group(1))
            elif line.startswith('+') and not line.startswith('+++'):
                content = line[1:].strip()
                if content:
                    prefix = "структура" if content.startswith(('def ', 'function ', 'class ')) else "добавил"
                    actions.append(f"{prefix}: '{content}' (строка {current_line})")
                current_line += 1
            elif line.startswith('-') and not line.startswith('---'):
                content = line[1:].strip()
                if content: actions.append(f"удалил: '{content}' (строка {current_line})")
        return actions

    def _log_event(self, path, actions, full_content):
        ts = time.strftime('%H:%M:%S')
        print(f"\n[{ts}] обновился: {path}")
        for action in actions: print(f"  -> {action}")
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps({"ts": ts, "file": path, "actions": actions, "content": full_content}, ensure_ascii=False) + '\n')
        except: pass

def main():
    project_path = get_clean_path()
    event_handler = DevReplayHandler(project_path)
    observer = Observer()
    observer.schedule(event_handler, project_path, recursive=True)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("\nзапись стоп.")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
