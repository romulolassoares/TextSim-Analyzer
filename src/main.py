import subprocess

def execute_streamlit():
    # This is the entry point for the Streamlit app
    subprocess.run(["streamlit", "run", "streamlit_ui.py"])

if __name__ == '__main__':
    try:
        execute_streamlit()
    except Exception as e:
        print(e)
