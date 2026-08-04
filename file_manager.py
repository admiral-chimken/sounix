from pathlib import Path

def expand_path(path):
    return Path(path).expanduser().resolve()


def list_files(path): 

    folder = expand_path(path)

    if not folder.exists():
         
        return f"sounix: '(folder)' is not a folder"

    if not folder.is_dir():
       return f"sounix: '(folder)' is not a folder"



    items = sorted(folder.iterdir())
    

    if not items:
        return f"sounix: '(folder)' is empty"

    lines = [f"sounix files in (folder):"]

    for item in items:
   
        marker = "[Folder]" if item.is_dir() else "[File]"
      
        lines.append(f"{marker} {item.name}")

    return "\n".join(lines)


def make_folder (path): 
   
    folder = expand_path (path)

    if folder.exists():
       return f"sounix: '(folder)' already exists"

    try: 
        folder.mkdir(parents=True)
        return f"sounix: created folder '(folder) '."

    except Exception as error:
        return f"sounix: could not create folder: (error)"        
         
    (error)
