import sys
import os
import importlib.util

def run_challenge(directory):
    main_path = os.path.join(directory, "main.py")
    if not os.path.exists(main_path):
        print(f"No main.py found in {directory}")
        return
        
    os.system(f"python {main_path}")

def main():
   if len(sys.argv) < 2:
       print("Please provide at least one directory name")
       return
   
   for directory in sys.argv[1:]:
       print(f"\nRunning {directory}:")
       run_challenge(directory)

if __name__ == "__main__":
   os.chdir(os.path.dirname(__file__))
   main()