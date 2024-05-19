from setuptools import setup, find_namespace_packages

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="crossword_puzzle",
    version="1.2.75",
    author="Tomas Vana",
    url="https://github.com/tomasvana10/crossword_puzzle",
    description="Select, generate and play always-unique crosswords.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(exclude=["venv", "venv.*"]),
    license="MIT",
    platforms="any",
    include_package_data=True,
    install_requires=[
        "Babel",
        "customtkinter",
        "Flask",
        "flask_babel",
        "Pillow",
        "regex"
    ],
    entry_points={
        "gui_scripts": [
            "crossword-ctk = crossword_puzzle.main:start"
        ]
    },
    classifiers=[
        "Topic :: Multimedia",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: JavaScript",
        "Topic :: Text Processing :: Markup :: HTML",
        "Framework :: Flask",
        "Topic :: Software Development :: Localization",
        "Topic :: Education",
        "Topic :: Games/Entertainment"
    ]
)
