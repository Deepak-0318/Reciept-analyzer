from setuptools import setup, find_packages

setup(
    name="receipt_analyzer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'pytesseract',
        'Pillow',
        'python-dateutil',
        'pdfplumber',
        'sqlalchemy',
        'pandas',
        'opencv-python',
    ],
)
