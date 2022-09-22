from setuptools import setup, find_packages

setup(
    name='mobi_router',
    version='1.0',
    author='mobigen',
    author_email='cbccbs@mobigen.co.kr',
    python_requires='>=3.6',

    packages=find_packages(exclude=['docs', 'tests*', '__pycache__/']),
    # packages=['ConnectManager']
)
