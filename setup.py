import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="json-objects",
    version="0.0.1",
    author="Yoram Abenhaim",
    author_email="yoram487@gmail.com",
    description="""
        load json text that can contain values in the form of an object or method. Example of a valid extended json string: '{"myObject": myClass(argument=5),"mymethod":sum([22,33])}"
        * It is preloaded to recognize built-in functions and classes.
        * you can register methods or classes to be recognized
        * When the class is not recognize it returns an Anonymous object ... which can then be applied to a real class by calling 'call' method.    
    """,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yoram487/json-objects",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",        
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        'Topic :: Software Development :: Libraries :: Json'
    ],
)