import os
import lizard

def get_all_cs_files(root_dir):
    cs_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".cs"):
                cs_files.append(os.path.join(root, file))
    return cs_files

def analyze_file(file_path):
    metrics = lizard.analyze_file(file_path)
    loc = metrics.nloc
    complexity = metrics.average_cyclomatic_complexity
    function_count = len(metrics.function_list)
    
    is_interface = False
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "interface" in line:
                is_interface = True
                break
    
    if is_interface:
        with open(file_path, "r", encoding="utf-8") as f:
            interface_methods = [line for line in f if any(modifier in line for modifier in ["public", "private", "protected", "internal"]) and "(" in line and ")" in line and not "class" in line]
            function_count = len(interface_methods)
    
    return loc, complexity, function_count

def analyze_all_files(cs_files):
    results = []
    total_loc = 0
    total_function_count = 0
    
    for file_path in cs_files:
        try:
            loc, complexity, function_count = analyze_file(file_path)
            total_loc += loc
            total_function_count += function_count
            results.append({
                "File": file_path,
                "LOC": loc,
                "Complexity": complexity,
                "Function Count": function_count
            })
        except Exception as e:
            print(f"Fehler bei der Analyse von {file_path}: {e}")
    
    return results, total_loc, total_function_count

def calculate_averages(results):
    if not results:
        return {}
    avg_loc = sum(r["LOC"] for r in results) / len(results)
    avg_complexity = sum(r["Complexity"] for r in results) / len(results)
    avg_function_count = sum(r["Function Count"] for r in results) / len(results)
    return {
        "Average LOC": avg_loc,
        "Average Complexity": avg_complexity,
        "Average Function Count": avg_function_count
    }

def save_results_to_file(results, averages, total_loc, total_function_count, filename):
    os.makedirs("./reports", exist_ok=True)
    filepath = os.path.join("./reports", filename)
    
    with open(filepath, "w") as f:
        f.write("Durchschnittswerte:\n")
        for key, value in averages.items():
            f.write(f"{key}: {value:.2f}\n")
        
        f.write(f"\nTotal LOC: {total_loc}\n")
        f.write(f"Totatl Function Count: {total_function_count}\n")
        
        f.write("\nEinzelne File-Analysen:\n")
        for result in results:
            f.write(f"File: {result['File']}\n")
            f.write(f"  LOC: {result['LOC']}\n")
            f.write(f"  Complexity: {result['Complexity']:.2f}\n")
            f.write(f"  Function Count: {result['Function Count']}\n")
            f.write("-" * 40 + "\n")
    
    print(f"Analyseergebnisse wurden in '{filepath}' gespeichert.")

if __name__ == "__main__":
    project_dir = input("Bitte gib den Pfad der zu analysierenden Dateien an: ")
    output_filename = input("Gib den Namen der Ergebnisdatei an (z.B. 'analysis_results.txt'): ")
    
    cs_files = get_all_cs_files(project_dir)
    if not cs_files:
        print("Keine C#-Dateien gefunden.")
    else:
        results, total_loc, total_function_count = analyze_all_files(cs_files)
        averages = calculate_averages(results)
        save_results_to_file(results, averages, total_loc, total_function_count, output_filename)
