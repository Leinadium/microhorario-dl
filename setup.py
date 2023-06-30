from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding='utf-8')

setup(
    name='microhorario-dl',
    version='1.4.1',
    description='PUC-Rio Microhorario Downloader',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Leinadium/microhorario-dl',
    author='Daniel Guimarães <github@Leinadium>',
    author_email='daniel.sch.guima@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "beautifulsoup4>=4",
        "requests>=2"
    ],
    python_requires=">3.7",
    project_urls={
        "Bug Reports": "https://github.com/Leinadium/microhorario-dl/issues",
        "Source": "https://github.com/Leinadium/microhorario-dl/"
    }
)
