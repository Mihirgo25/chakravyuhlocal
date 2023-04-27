from setuptools import setup, find_packages

def get_requirements():
    try:
        f = open("requirements.txt")
    except Exception:
        f = open('../requirements.txt')
    
    return [x.strip() for x in f.read().split("\n") if not x.startswith("#")]


install_requires = get_requirements()

setup(
    name='app',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
   entry_points={
        "console_scripts": ["envision = cli:entrypoint"]}
)