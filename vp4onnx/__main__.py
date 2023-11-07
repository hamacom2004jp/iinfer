import os


HOME_DIR = os.path.expanduser("~")

if __name__ == "__main__":
    from vp4onnx.app import app
    app.main(HOME_DIR)
