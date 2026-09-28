import re
from pathlib import Path

def remove_docstrings(source_code: str) -> str:
    return re.sub(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', '', source_code)

def flatten_code_for_llm(
    directories_to_scan: list[str],
    files_to_include: list[str],
    output_dir: str,
    base_filename: str,
    skip_dirs: list[str] | None = None
) -> None:
    if skip_dirs is None:
        skip_dirs = []

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    path_all = out_dir / f"{base_filename}_all.txt"
    path_clean = out_dir / f"{base_filename}_clean.txt"
    
    with open(path_all, "w", encoding="utf-8") as f_all, \
         open(path_clean, "w", encoding="utf-8") as f_clean:
        
        for file_name in files_to_include:
            file_path = Path(file_name)
            header = f"\n{'='*40}\nFile: {file_path.as_posix()}\n{'='*40}\n\n"
            f_all.write(header)
            f_clean.write(header)
            
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as in_file:
                        content = in_file.read()
                        f_all.write(content)
                        f_clean.write(content) 
                except Exception as e:
                    error_msg = f"# Error: {e}\n"
                    f_all.write(error_msg)
                    f_clean.write(error_msg)
            else:
                missing_msg = f"# File not found: {file_name}\n"
                f_all.write(missing_msg)
                f_clean.write(missing_msg)
            
            f_all.write("\n")
            f_clean.write("\n")
        
        for directory in directories_to_scan:
            source_path = Path(directory)
            if not source_path.exists():
                continue
            
            for py_file in source_path.rglob("*.py"):
                # Move the skip check inside the loop to test each file path
                if any(skip_dir in py_file.as_posix() for skip_dir in skip_dirs):
                    continue

                header = f"\n{'='*40}\nFile: {py_file.as_posix()}\n{'='*40}\n\n"
                f_all.write(header)
                f_clean.write(header)
                
                try:
                    with open(py_file, "r", encoding="utf-8") as in_file:
                        content = in_file.read()
                        f_all.write(content)
                        f_clean.write(remove_docstrings(content))
                except Exception as e:
                    error_msg = f"# Error: {e}\n"
                    f_all.write(error_msg)
                    f_clean.write(error_msg)
                
                f_all.write("\n")
                f_clean.write("\n")

if __name__ == "__main__":
    name = "mocaco" 
    directories_to_scan = ["src"]
    files_to_include = ["README.md"]
    skip_dirs = ["fastpia/tests", "fastpiagui/tests"]
    
    flatten_code_for_llm(
        directories_to_scan=directories_to_scan,
        files_to_include=files_to_include,
        output_dir="local",
        base_filename=name,
        skip_dirs=skip_dirs
    )