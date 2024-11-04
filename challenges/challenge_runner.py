import shutil
import sys
import os
import importlib.util
from pathlib import Path


def reset_workspace(path: Path):
    if (path / "template").exists:
        shutil.rmtree(path / "workspace", ignore_errors=True)
        shutil.copytree(path / "template", path / "workspace")

# def run_challenge(path: Path):
#     reset_workspace(path)
    
#     main_path = path / "main.py"
#     if not os.path.exists(main_path):
#         print(f"No main.py found in {path}")
#         return
        
#     os.system(f"python {main_path}")

def run_challenge(path: Path):
    original_dir = os.getcwd()
    reset_workspace(path)
    try:
        os.chdir(path)
        module = importlib.import_module(f"{path}.agent")
        #agent = module.get_agent()
        #module.evaluate(agent)
        module.run()
    except ImportError as e:
        print(f"Error importing {path}/main.py: {e}")
    except AttributeError as e:
        print(f"Missing required function in {path}/main.py: {e}")
    finally:
        os.chdir(original_dir)

def main():
   if len(sys.argv) < 2:
       print("Please provide at least one directory name")
       return
   
   for directory in sys.argv[1:]:
       print(f"\nRunning {directory}:")
       run_challenge(Path(directory))

if __name__ == "__main__":
   os.chdir(os.path.dirname(__file__))
   main()