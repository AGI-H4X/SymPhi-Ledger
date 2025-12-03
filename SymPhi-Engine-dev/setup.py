from setuptools import setup, find_packages

setup(
    name="gdk9",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["numpy"],
    extras_require={"dev": ["pytest"]},
    entry_points={
        "console_scripts": ["gdk9=gdk9.cli:main"]
    },
    python_requires=">=3.10",
    author="GDk9 Labs",
    description="Physics-aware symbolic implication kernel",
)
