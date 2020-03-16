from setuptools import setup

setup(
   name='sql_transfer',
   version='1.0',
   description='A useful module',
   author='Man Foo',
   author_email='foomail@foo.com',
   packages=['sql_transfer'],  #same as name
   install_requires=['SQLAlchemy', 'pandas'], #external packages as dependencies
)