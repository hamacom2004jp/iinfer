from iinfer import version
from setuptools import setup


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
    'eel',
    'motpy',
    'opencv-python',
    'Pillow',
    'pyyaml',
    'redis',
    'requests',
    'tabulate',
    'wheel'
]
PACKAGES = [
    'iinfer',
    'iinfer.app',
    'iinfer.app.predicts',
    'iinfer.app.postprocesses',
    'iinfer.datasets',
    'iinfer.docker'
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
RESORCE_TEXT_FILES = dict(iinfer=['*.yml', 'docker/*', 'datasets/**', 'licenses/**', 'web/**'])
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
    entry_points=dict(console_scripts=['iinfer=iinfer.app.app:main'])
)