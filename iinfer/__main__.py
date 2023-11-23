import os


HOME_DIR = os.path.expanduser("~")

if __name__ == "__main__":
    from iinfer.app import app
    app.main(HOME_DIR)
