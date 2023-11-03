from pathlib import Path
import argparse
import os


HOME_DIR = os.path.expanduser("~")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='python -m vp4onnx',
        description='This application generates modules to set up the application system.')
    
    parser.add_argument('--data',
                        help='Setting the data directory.',
                        default=Path(HOME_DIR) / ".vp4onnx")
    parser.add_argument('--boot_mode',
                        help='Setting the boot mode.',
                        choices=['cli', 'gui'],
                        default='cli')
    parser.add_argument('--boot_schema',
                        help='Setting the service url schema.',
                        default='localhost')
    parser.add_argument('--boot_host',
                        help='Setting the service url host.',
                        default='localhost')
    parser.add_argument('--boot_port',
                        help='Setting the service url port.',
                        default=8080)

    args = parser.parse_args()
    from vp4onnx.app import app
    app.main(Path(args.data), args.boot_mode, args.boot_schema, args.boot_host, args.boot_port)
