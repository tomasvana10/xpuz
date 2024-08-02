---
title: Home
---

![crossword banner](https://github.com/tomasvana10/xpuz/assets/124552709/370a11cb-540e-41c4-8917-5f5272da2ebd)
![licence](https://img.shields.io/badge/licence-MIT-green?style=flat?logo=licence)
[![PyPI version](https://img.shields.io/pypi/v/xpuz?style=flat-square)](https://pypi.org/project/xpuz/)
[![Publish to PyPI.org](https://github.com/tomasvana10/xpuz/actions/workflows/publish.yml/badge.svg)](https://github.com/tomasvana10/xpuz/actions/workflows/publish.yml)
[![release](https://img.shields.io/github/v/release/tomasvana10/xpuz?logo=github)](https://github.com/tomasvana10/xpuz/releases/latest)
[![issues](https://img.shields.io/github/issues-raw/tomasvana10/xpuz.svg?maxAge=25000)](https://github.com/tomasvana10/xpuz/issues)
[![CodeQL](https://github.com/tomasvana10/xpuz/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/tomasvana10/xpuz/actions/workflows/github-code-scanning/codeql)
[![Tests](https://github.com/tomasvana10/xpuz/actions/workflows/tox-tests.yml/badge.svg)](https://github.com/tomasvana10/xpuz/actions/workflows/tox-tests.yml)

## About
[xpuz](https://github.com/tomasvana10/xpuz) is a GUI/web package built with `CustomTkinter` and `Flask`. It allows you to select a predefined or customised set of words to procedurally generate a crossword from, and view it in a locally hosted `Flask` web app.

[Download the latest source code :material-download:](https://github.com/tomasvana10/xpuz/releases/latest){ .md-button .md-button--primary }

[Play a demo of `xpuz` on your browser :material-controller:](https://tomasvana10.github.io/){ .md-button }
  
## Why `xpuz`?
There are several features of `xpuz` that makes it an ideal software for learning or to just have some fun when you're bored:

1. It provides several pre-made sets of crosswords for academic topics, making it ideal for learning and studying.
2. It prioritises ergonomics above all else.
3. It provides the ability to design your own word sets, as well as export generated crosswords to either PDF or ipuz (an open-source version of the proprietary file format `puz`). This allows you to export your generated crosswords and complete them in a different player, such as `Exolve`, if you desire.
4. It implements various inclusivity features, such as:

    - The ability to choose from over 95 languages
    - Tab and zooming support for the interactive web application
    - Light and dark mode 
    - Scaling
    - Cross-platform compatibility
    - Extensive browser support
    - Crossword difficulties

## Tested Python Versions
Operating System | Version |
------- | ------- |
Windows | >=3.7
MacOS | >=3.8
Linux | >=3.8

## Requirements
### Hardware
  - **RAM**: >120MB (GUI only), >500MB (GUI and browser to play crossword)
  - **CPU**: Any
  - **Storage**: >30MB available space (the program and its dependencies)

### Software
  - **OS**: Windows, MacOS, Linux
  - **Browser**: Not Internet Explorer
  - **Additional**: Python and pip (see [Getting Started](installation.md))

## Limitations
- Right-to-left scripts are not supported.
- Mobile devices are not supported.
- Translations are made with a [translation API](https://cloud.google.com/dotnet/docs/reference/Google.Cloud.Translation.V2/latest), and therefore might be inaccurate.
- Generated crosswords may occasionally have a few missing words.
- If your OS scaling is higher than the default, the web application will likely be too big. Read [Troubleshooting](https://github.com/tomasvana10/xpuz/wiki/Troubleshooting) for more information.

## Crossword categories
`xpuz` comes with 4 main categories by default, each with their own topics (which often have multiple difficulties): 
??? note "Computer Science"
    - Booleans
    - Hardware
    - Programming
    - Python
    - Cybersecurity
    - AI

??? note "Geography"
    - Capitals
    - Countries by Landmarks
    - US State Capitals
  
??? note "Mathematics"
    - Geometry
    - Probability
    - Trigonometry
    - Calculus
    - Combinatorics
     
??? note "Science"
    - General Science
    - Physics
    - Biology
    - Chemistry