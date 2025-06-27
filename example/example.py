from workflowpy.magic import *

thresholds = [90, 80, 60, 0]
names = ['wonderful', 'great', 'okay', 'terrible']

grade = int(input("Please enter your grade: "))

for i, threshold in enumerate(thresholds):
    if grade > threshold:
        print(f"You are doing {names[i]}!")
        break
