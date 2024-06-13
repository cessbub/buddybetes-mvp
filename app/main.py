import os
import sys

# Add the app directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

import run  # Importing the run.py script from the app directory

# Directly call the main function if necessary
if __name__ == "__main__":
    run.main()
