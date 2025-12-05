from setuptools import setup, find_packages

setup(
    name="Research_First_Sourcer_Automation",
    version="1.0.1",
    packages=find_packages(),
    install_requires=[
        "openai>=2.9.0",
        "pandas>=2.3.0",
        "python-dotenv>=1.0.0",
        "rich>=14.0.0"
    ],
    author="Dave Mendoza",
    description="Research-First Sourcer Automation — integrated multi-phase AI Talent Engine (Phases 6–8)",
    python_requires=">=3.10",
)
