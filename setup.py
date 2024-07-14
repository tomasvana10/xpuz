from setuptools import find_namespace_packages, setup


setup(
    name="xpuz",
    version="2.2.100",  # If I import xpuz.version.__version__, 
                        # setuptools fails to build the project for some reason
    author="Tomas Vana",
    url="https://github.com/tomasvana10/xpuz",
    description="Design and play procedurally generated crosswords",
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
        "pywebview",
    ],
    entry_points={
        "gui_scripts": [
            "xpuz-ctk = xpuz.__main__:main"
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
