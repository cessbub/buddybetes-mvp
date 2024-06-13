import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

if __name__ == "__main__":
    import streamlit.cli as stcli
    sys.argv = ["streamlit", "run", "app/run.py"]
    sys.exit(stcli.main())
