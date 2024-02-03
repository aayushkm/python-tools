#Cewl
import random
from random import randint
import sys
import re

data = sys.stdin.readlines()
list = ["!",".","*",".","*","&"]


for row in data:
    num = randint(1,999)
    num = str(num)
    ran = random.choice(list)
    row = re.sub("\n", "", row)
    new_word = ran+row+num
    print(new_word[1:]+new_word[0])
