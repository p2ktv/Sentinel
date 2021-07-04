from setuptools import setup, find_packages



setup(
    name="sentinel-python",
    version="0.0.2",
    author="xezzz",
    author_email="ezzz.btw@gmail.com",
    description="Package for using Discord slash commands",
    packages=find_packages(),
    install_requires=["websocket-client", "aiohttp"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)