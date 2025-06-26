from workflowpy import *

thresholds = [90, 80, 60, 0]

names = ['wonderful', 'great', 'okay', 'terrible']


for _ in range(99):
    grade = int(input("Please enter your grade: "))
    for i, threshold in enumerate(thresholds):
        if grade > threshold:
            print(f"You are doing {names[i]}! You are {100 - grade} points away from perfect!")
            break
