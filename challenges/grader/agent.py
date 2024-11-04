import os
#from util import compare_results, reset_workspace
from langur import Langur
from langur.connectors import Workspace
import shutil
import pandas as pd


EXPECTED_RESULT = pd.DataFrame({
    "First Name": ["Ethan", "Mia", "Ava", "Noah", "Bob"],
    "Last Name": ["Caldwell", "Kensington", "Harlow", "Winslow", "Smith"],
    "Points": [1, 4, 5, 5, 3]
})

def compare_results():
    actual_df = pd.read_csv("./workspace/grades.csv")
    print("\nActual:")
    print(actual_df)
    print("\nExpected:")
    print(EXPECTED_RESULT)
    
    are_equal = actual_df.equals(EXPECTED_RESULT)
    if not are_equal:
        print("\nDifferences found!")
    
    return are_equal

def run():
    agent = Langur("Grade quizzes")
    agent.use(Workspace(path="./workspace"))
    agent.run()

    assert compare_results()

