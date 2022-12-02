from setuptools import setup, find_packages

setup(
    name="mobigen_service",
    version="0.5",
    author="mobigen",
    author_email="cbccbs@mobigen.co.kr",
    python_requires=">=3.6",
    packages=find_packages(exclude=["docs", "tests*", "__pycache__/"]),
)
