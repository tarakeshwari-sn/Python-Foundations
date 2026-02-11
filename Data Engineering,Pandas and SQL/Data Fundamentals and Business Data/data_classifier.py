import os,csv,json,shutil

incoming_dir=r"C:\Users\Tarakeshwari\OneDrive\Desktop\Python-Foundations\Data Engineering .Pandas and SQL\incoming"
processed_dir="processed"

def is_structured_csv(file_path):
    try:
        with open(file_path,"r",encoding="utf-8") as f:
            reader=csv.reader(f)
            rows=list(reader)
            if len(rows)<2:
                return False
            column_count=len(rows[0])
            return all(len(row)==column_count for row in rows)
    except:
        return False

def is_semi_structured_json(file_path):
    try:
        with open(file_path,"r",encoding="utf-8") as f:
            json.load(f)
        return True
    except:
        return False

def statistical_check(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines=f.readlines()

        if len(lines)<2:
            return False

        delimiter_counts=[line.count(",") for line in lines]
        variance=max(delimiter_counts)-min(delimiter_counts)

        return variance == 0 and delimiter_counts[0] > 0
    except:
        return False

def classify_file(file_path):
    if is_structured_csv(file_path):
        return "structured"
    elif is_semi_structured_json(file_path):
        return "semi_structured"
    elif statistical_check(file_path):
        return "structured"
    else:
        return "unstructured"

def automate():
    for file in os.listdir(incoming_dir):
        file_path=os.path.join(incoming_dir, file)

        if os.path.isfile(file_path):
            category=classify_file(file_path)

            destination=os.path.join(processed_dir,category)
            os.makedirs(destination,exist_ok=True)

            shutil.move(file_path, destination)
            print(f"{file} is {category}")

if __name__ == "__main__":
    automate()
