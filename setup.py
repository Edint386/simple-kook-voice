from setuptools import setup, find_packages

setup(
    name='kookvoice',  # 你的 SDK 的名称
    version='0.1.0',  # 初始版本号
    description='A Python SDK for kook music bot',  # 项目简介
    long_description=open('README.md',encoding='utf-8').read(),
    long_description_content_type='text/markdown',  # README 文件的格式
    author='xsNight',  # 你的名字
    author_email='jason62570127@gmail.com',  # 你的联系邮箱
    url='https://github.com/Edint386/simple-kook-voice',  # 项目的主页（通常是 GitHub）
    packages=find_packages(),  # 自动找到包目录
    install_requires=[  # 列出你的包依赖
        "aiohttp",
    ],
    classifiers=[  # 关于包的分类信息
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',  # 支持的 Python 版本
)