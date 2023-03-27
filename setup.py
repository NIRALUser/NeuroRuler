from setuptools import setup

APP = ["gui.py"]
OPTIONS = {"argv_emulation": True}

setup(app=APP, options={"py2app": OPTIONS}, setup_requires=["py2app"])

if __name__ == "__main__":
    setup()
