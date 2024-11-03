from iinfer import version
from pathlib import Path
from setuptools import setup
from setuptools.command.install import install
import platform


DESCRIPTION = 'iinfer: An application that executes AI model files in onnx or mmlab format.'
NAME = 'iinfer'
AUTHOR = 'hamacom2004jp'
AUTHOR_EMAIL = 'hamacom2004jp@gmail.com'
URL = version.__srcurl__
LICENSE = 'MIT'
DOWNLOAD_URL = URL
VERSION = version.__version__
PYTHON_REQUIRES = '>=3.8'
INSTALL_REQUIRES = [
    'argcomplete',
    'async_timeout',
    'beaker',
    'bottle',
    'bottle_websocket',
    'motpy',
    'opencv-python',
    'numpy',
    'Pillow',
    'pyyaml',
    'redis',
    'requests',
    'tabulate',
    'urllib3',
    'wheel',
]
PACKAGES = [
    'iinfer',
    'iinfer.app',
    'iinfer.app.commons',
    'iinfer.app.injections',
    'iinfer.app.postprocesses',
    'iinfer.app.predicts',
    'iinfer.app.trains',
    'iinfer.docker',
    'iinfer.extensions'
]
KEYWORDS = 'onnxruntime predict inference image ai model'
CLASSIFIERS=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: Japanese',
    'Programming Language :: Python',
    'Topic :: Utilities'
]
with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()
LONG_DESCRIPTION = readme
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
RESORCE_TEXT_FILES = dict(iinfer=['*.yml', 'extensions/*', 'extensions/*/*', 'extensions/*/*/*',
                                  'docker/*', 'docker/*/*', 'licenses/*',
                                  'tools/datas/*', 'tools/datas/*/*',
                                  'web/*', 'web/*/*', 'web/*/*/*', 'web/*/*/*/*', 'web/*/*/*/*/*'])
EXCLUDE_RESORCE_TEXT_FILES =dict(iinfer=['extensions/data/*.json', 'extensions/data/*/*.jpg', 'extensions/data/*/*.svg'])
class CustomInstallCommand(install):
    def run(self):
        super().run()
        if platform.system() != 'Linux':
            return
        bashrc = Path.home() / '.bashrc'
        if not bashrc.exists():
            return
        CMD = 'eval "$(register-python-argcomplete iinfer)"'
        with open(bashrc, 'r') as fp:
            for line in fp:
                if line == CMD:
                    return
        with open(bashrc, 'a') as fp:
            fp.write('\n'+CMD)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    python_requires=PYTHON_REQUIRES,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    url=URL,
    download_url=URL,
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    license=LICENSE,
    keywords=KEYWORDS,
    install_requires=INSTALL_REQUIRES,
    package_data=RESORCE_TEXT_FILES,
    include_package_data=True,
    exclude_package_data=EXCLUDE_RESORCE_TEXT_FILES,
    entry_points=dict(console_scripts=['iinfer=iinfer.app.app:main']),
    cmdclass={'install': CustomInstallCommand},
)