from setuptools import find_namespace_packages, setup


setup(
    name="crossword_puzzle",
    version="2.2.93",  # If I import crossword_puzzle.version.__version__, 
                       # setuptools fails to build the project for some reason
    author="Tomas Vana",
    url="https://github.com/tomasvana10/crossword_puzzle",
    description="Select, generate and play always-unique crosswords.",
    long_description=open("README.md").read(),
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
        "regex",
        "platformdirs",
        "pathvalidate",
        "CTkToolTip",
    ],
    entry_points={
        "gui_scripts": [
            "crossword-ctk = crossword_puzzle.main:main"
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
