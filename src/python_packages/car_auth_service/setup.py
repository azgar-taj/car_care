from setuptools import setup, find_packages

setup(
    name='car_auth_service',
    version='1.0.0',
    description='Python package for car service authentication',
    author='Abdul Azgar Taj',
    author_email='aat10@iitbbs.ac.in',
    packages=find_packages(),
    install_requires=[
        # Add any dependencies your package requires here
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)