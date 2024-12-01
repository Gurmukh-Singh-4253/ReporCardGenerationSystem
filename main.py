import pandas as pd
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
import subprocess
import os


# Some fixed rules for the CSV:
# Must have a Name column, roll number column,
# and the rest of the columns would be subjects and marks.
path = input("Enter the path to the CSV file: ")

data = pd.read_csv(path)
subjects = [x for x in data.columns if x != "name" and x != "roll_no"]

for i in subjects:
    data[f'rank_{i}'] = data[i].rank(method='min', ascending=False)
    data[f'percentile_{i}'] = (len(data) - data[f'rank_{i}'])/len(data) * 100

data['average_score'] = data[subjects].mean(axis=1)
data['rank'] = data['average_score'].rank(method="min", ascending=False)
data['percentile'] = (len(data) - data['rank']) / len(data) * 100


env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.tex')

function_dict = {"min": min, "int": int}
template.globals.update(function_dict)

os.system("mkdir out || rm out/*")
os.system("mkdir charts || rm charts/*")

# Generating Graphs...
for i in subjects:
    counts, bins, patches = plt.hist(data[i],
                                     bins=[x for x in range(0, int(max(data[i]))+5, 5)],
                                     color='skyblue'
                                     )

    for j in range(len(patches)):
        for k in range(j):
            patches[k].set_facecolor('skyblue')
        patches[j].set_facecolor('blue')

        plt.xlabel("Marks")
        plt.ylabel("Frequency")
        plt.savefig(f"charts/{i}_{j}.png")
    plt.cla()

counts, bins, patches = plt.hist(data['average_score'], bins=[x for x in range(0, max(data[i])+5, 5)], color='pink')
for i in range(len(patches)):
    for j in range(i):
        patches[j].set_facecolor('pink')
    patches[i].set_facecolor('red')
    plt.xlabel("Marks")
    plt.ylabel("Frequency")
    plt.savefig(f"charts/average_score_{i}.png")
plt.cla()


for index, row in data.iterrows():
    latex_code = template.render(
        name=row['name'],
        roll_no=row['roll_no'],
        length=len(subjects),
        subjects=subjects,
        scores=row[subjects],
        subrank=row[[f"rank_{i}" for i in subjects]],
        subpercentile=row[[f'percentile_{i}' for i in subjects]],

        average_score=row['average_score'],
        rank=row['rank'],
        percentile=row['percentile']
    )

    with open(f"out/report_card_{row['roll_no']}.tex", 'w') as f:
        f.write(latex_code)

    # Compile LaTeX
    subprocess.run(['pdflatex', '-output-directory=out', f"out/report_card_{row['roll_no']}.tex"])
    subprocess.run(['rm', f'out/report_card_{row['roll_no']}.aux'])
    subprocess.run(['rm', f'out/report_card_{row['roll_no']}.log'])
    subprocess.run(['rm', f'out/report_card_{row['roll_no']}.tex'])

summary = []
for i in subjects:
    summary.append(f"Statistics for subject {i}\n")
    summary.append(f"Mean: {data[i].mean()}\n")
    summary.append(f"Median: {data[i].median()}\n")
    summary.append(f"Standard deviation: {data[i].std()}\n")
    summary.append("\n")

summary.append("Overall Statistics\n")
summary.append(f"Mean: {data['average_score'].mean()}\n")
summary.append(f"Median: {data['average_score'].median()}\n")
summary.append(f"Standard deviation: {data['average_score'].std()}\n")

summary.append("\n")

summary.append("Top Students:\n")
summary.append(str(data[['roll_no', 'name'] + ["rank_"+x for x in subjects] + ['rank', 'percentile']].sort_values(by="percentile", ascending=False).to_string()))


with open("out/Comprehensive_analysis.txt", 'w') as f:
    f.writelines(summary)
    f.close()
