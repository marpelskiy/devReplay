import os
import json

def get_clean_path():
    p = input("где проект? (Enter если тут): ").strip()
    if not p or p == '.': return os.getcwd()
    if p.startswith('home/'): p = '/' + p
    return os.path.abspath(os.path.expanduser(p))

def main():
    project_path = get_clean_path()
    log_file = os.path.join(project_path, '.dev-replay', 'log.jsonl')

    if not os.path.exists(log_file):
        print("логов пока нет. сначала запусти dev log.")
        return

    events = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                if data.get('file') != '[TERMINAL]':
                    events.append(data)
    except Exception:
        print("че-то не так с файлом логов. возможно он поврежден.")
        return

    if not events:
        print("история пуста.")
        return

    print("\nпоследние 15 действий:\n")
    for e in events[-15:]:
        time_val = e.get('ts', '??:??')
        file_name = os.path.basename(e.get('file', ''))
        actions = e.get('actions', [])
        if actions:
            first_act = actions[0][:60] + "..." if len(actions[0]) > 60 else actions[0]
            print(f"[{time_val}] {file_name} -> {first_act}")
    print("")

if __name__ == "__main__":
    main()
