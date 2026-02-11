import threading
from pathlib import Path

results=[]
lock=threading.Lock()

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    data = {"file":file_path.name,"lines":text.count("\n")+ 1,
            "words":len(text.split()),"chars":len(text)}
    with lock:
        results.append(data)

    print(f"Processed: {file_path.name}")

def main():
    threads = []
    folder = Path("downloads")

    for file in folder.glob("*.txt"):
        t = threading.Thread(target=process_file, args=(file,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\nSummary:")
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
