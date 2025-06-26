from workflowpy import *

names = {'David': 'owner', 'Foo': 'editor'}

name: str = input('What is your name?')

if name in names:
    print(f"You're in, {name}, as an {names[name]}!")
