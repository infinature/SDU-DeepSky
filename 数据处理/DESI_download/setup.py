from setuptools import setup, find_packages
import os
import re

# Function to get version from __init__.py using regex
def get_version_from_init():
    init_py_path = os.path.join(os.path.dirname(__file__), 'desi_data_processor', '__init__.py')
    with open(init_py_path, 'r') as f:
        init_py_content = f.read()
    match = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", init_py_content, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string in desi_data_processor/__init__.py")

# 从 requirements.txt 读取依赖
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# 从 README.md 读取长描述
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='desi_data_processor',
    version=get_version_from_init(),
    author='mengjunyu',
    author_email='202300800677@mail.sdu.edu.cn',
    description='一个处理DESI天文数据的Python库',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/qintianjian-lab/2025-undergrad-astro-dataprocessing',
    packages=find_packages(exclude=['tests*', 'docs*', 'examples*']),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
    python_requires='>=3.8',
    keywords='desi astronomy fits data processing cosmology spectroscopy',
    project_urls={
        'Bug Reports': 'https://github.com/qintianjian-lab/2025-undergrad-astro-dataprocessing/issues',
        'Source': 'https://github.com/qintianjian-lab/2025-undergrad-astro-dataprocessing/',
        'Documentation': 'https://data.desi.lbl.gov/doc/', # 指向官方DESI文档
    },
    # 如果有命令行脚本，可以在这里配置
    # entry_points={
    #     'console_scripts': [
    #         'desi_process=desi_data_processor.cli:main', # 假设有一个cli.py
    #     ],
    # },
)
