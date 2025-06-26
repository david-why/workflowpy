from workflowpy import *

names: dict = {'David': 'owner', 'Foo': 'editor'}

name: str = input('What is your name?')

if name in names:
    print(f"You're in, {name}, as an {names[name]}!")
elif name == 'What':
    print('What??')
else:
    print('Who the heck are you?')
