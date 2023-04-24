import subprocess
import os
from carddict import cardDict

os.chdir("resources")
subprocess.run("pdftoppm -png -r 40 primecards-individual.pdf out", shell=True)

i = 1
for number in range(10):
    os.rename(f"out-{i:03}.png", f"{number}.png")
    i += 1
    for symbol in cardDict[number]:
        os.rename(f"out-{i:03}.png", f"{number}({symbol}).png")
        i += 1

subprocess.run("pdftoppm -png -r 40 boardsquares-individual.pdf out", shell=True)
for i in range(100):
    os.rename(f"out-{i+1:03}.png", f"square-{i}.png")