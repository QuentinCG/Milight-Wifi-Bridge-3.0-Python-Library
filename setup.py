from setuptools import setup
import io

with io.open('README.md', 'r', encoding='utf-8') as readme_file:
  readme = readme_file.read()

setup(
    name='MilightWifiBridge',
    version='2.0',
    description='Milight Wifi Bridge 3.0 controller for LimitlessLED Wifi Bridge v6.0 protocol (Light ON/OFF, change color/mode/brightness/saturation, link/unlink)',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/QuentinCG/Milight-Wifi-Bridge-3.0-Python-Library',
    author='Quentin Comte-Gaz',
    author_email='quentin@comte-gaz.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS X',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='milight bulbs home automation limitlessled ibox link unlink light night white color saturation brightness disco mode speed mac',
    packages=["MilightWifiBridge"],
    platforms='any',
    install_requires=[],
    tests_require=["mock"],
    test_suite="tests",
)
