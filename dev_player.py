import os
import json
import shutil

def get_clean_path():
    p = input("где проект? (Enter если тут): ").strip()
    if not p or p == '.': return os.getcwd()
    if p.startswith('home/'): p = '/' + p
    return os.path.abspath(os.path.expanduser(p))

def replay_time(project_path, target_time):
    replay_dir = os.path.join(project_path, '.dev-replay')
    log_file = os.path.join(replay_dir, 'log.jsonl')
    machine_dir = os.path.join(replay_dir, 'time_machine')

    if not os.path.exists(log_file):
        print("логов нет. ты точно запускал dev log тут?")
        return

    file_states = {}
    matched = 0
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                if data.get('file') == '[TERMINAL]' or 'content' not in data: continue
                if data['ts'] <= target_time:
                    matched += 1
                    file_states[data['file']] = data['content']
    except Exception:
        print("ошибка при чтении логов. проверь файл log.jsonl")
        return

    if not file_states:
        print("на это время ничего нет. попробуй попозже.")
        return

    try:
        if os.path.exists(machine_dir):
            shutil.rmtree(machine_dir)
        os.makedirs(machine_dir, exist_ok=True)

        for filepath, content in file_states.items():
            target_path = os.path.join(machine_dir, os.path.basename(filepath))
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
    except Exception:
        print("не вышло собрать файлы. проверь права доступа.")
        return

    print(f"\nготово. восстановил {matched} слепков.")
    print(f"твой код из прошлого лежит тут: {machine_dir}")

def main():
    project_path = get_clean_path()
    target_time = input("на какое время мотаем? (например 20:35): ").strip()
    
    if len(target_time) == 5: target_time += ":59"
        
    replay_time(project_path, target_time)

if __name__ == "__main__":
    main()
