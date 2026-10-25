import pandas as pd
import numpy as np
import random

r=int(input("Please enter the desired number of generations :"))
# ==========================================
# 1. Population Initialization
# ==========================================
x=input("Enter the total jobs: ")
pop= {
    i: [str(num) for num in random.sample(range(1, int(x)+1), int(x))]
    for i in range(1, 11)
}

# In thử kết quả để kiểm tra
for key in pop:
    print (f"individual {key}: {pop[key]}\n")



# ==========================================
# 2. file path entering and sheet choosing
# ==========================================
#"Enter the path to the Excel file:"
file_path = r"C:\Users\admin\Downloads\Book (1).xlsx"
file_path = file_path.replace("\\", "/").strip('"')

excel_file = pd.ExcelFile(file_path)
sheet_names = excel_file.sheet_names

print("\nList of sheets in the file:")
for i, sheet in enumerate(sheet_names):
    print(f"{i} - {sheet}")

while True:
    try:
        print("\nPlease select the sheet you want to scan, based on its corresponding number:")
        chosen_sheet = int(input())
        print(f"Selected sheet: {sheet_names[chosen_sheet]}")

        print("Please enter your header row - Based on the excel file (e.g., 1 for row 1):")
        selected_row = int(input())

        df = pd.read_excel(
            file_path,
            sheet_name=sheet_names[chosen_sheet],
            header=selected_row - 1
        )
        print("\n--> Read sheet successfully!")
        break
    except Exception as e:
        print(f"Error reading sheet: {e}. Please try again.")
# ==========================================
# 3. Fitness function
# ==========================================

jobDict={}
for job, pt, dd in zip(df['job'], df['processing_time'], df['Due_date']):
    if ('pt'+str(job)) not in jobDict:
        jobDict['pt'+str(job)]=pt
    else:
        jobDict['pt'+str(job)]+=pt
    if ('dd' +str(job)) not in jobDict:
        jobDict['dd' +str(job)]=dd
    else:
        jobDict['dd' +str(job)]+=dd
print (jobDict)
fn={} #Finding the maximum delay in a job for each individual.
for k in pop:
    C=0
    for j in pop[k]:
        C+=jobDict['pt'+str(j)]
        if k not in fn:
            fn[k]=max(C-jobDict['dd'+str(j)]*24*60,0)/(24*60)
        else:
            if max(C-jobDict['dd'+str(j)]*24*60,0)/(24*60) > fn[k]:
                fn[k]=max(C-jobDict['dd'+str(j)]*24*60,0)/(24*60)
    print (f"fitness of individual {k}: " + str(fn[k]))

g=1
z=100000
while g<=r:
    print ("""
    ====="""+f"GEN {g}"+"""====
    """)
    i=1000000
    k=1000000
    for i1 in fn:
        if fn[i1]<i:
            i=fn[i1]
            dad=i1
    for k1 in fn:
        if i<fn[k1]<k:
            k=fn[k1]
            mom=k1
    print (f"the best couple is individual {dad} L.max = {i} and individual {mom} L.max = {k}.")
# ==========================================
# 4. Selection
# ==========================================
    def crossover(Dad, Mom):
        size=len(Dad)
        #Randomly select 2 intersection points and arrange them in ascending order.
        p1, p2 = sorted(random.sample(range(size), 2))
        child1 = [None] * size
        child2 = [None] * size
        # Copy the section between p1 and p2 from the respective parent.
        child1[p1:p2+1] = Dad[p1:p2+1]
        child2[p1:p2+1] = Mom[p1:p2+1]
        # Get a list of elements not yet in the child (keeping the order of parent_source)
        rem1 = [item for item in Mom if item not in child1]
        rem2 = [item for item in Dad if item not in child2]
        # Điền trực tiếp vào các vị trí None còn trống
        idx1, idx2 = 0, 0
        for i in range(size):
            if child1[i] is None:
                child1[i] = rem1[idx1]
                idx1 += 1
            if child2[i] is None:
                child2[i] = rem2[idx2]
                idx2 += 1
        return child1, child2, p1, p2
    pop[dad], pop[mom], p1, p2 = crossover(pop[dad], pop[mom])
    print( f"The two crossover positions were chosen randomly as follows: point 1 - {p1} and point 2 - {p2}")
    def mutation (child):
        child_mutated = child.copy()
        size=len(child)
        #Randomly select 2 mutation points.
        p1, p2 = sorted(random.sample(range(size), 2))
        child_mutated[p1], child_mutated[p2] = child_mutated[p2], child_mutated[p1]
        return child_mutated, p1, p2
    pop[dad], p1, p2 = mutation(pop[dad])
    print( f"The two mutation positions were chosen randomly for individual {dad}: point 1 - {p1} and point 2 - {p2}")
    pop[mom], p1, p2 = mutation(pop[mom])
    print( f"The two mutation positions were chosen randomly for individual {mom}: point 1 - {p1} and point 2 - {p2}")
    C=0
    for j in pop[dad]:
        C+=jobDict['pt'+str(j)]
        if max(C-jobDict['dd'+str(j)]*24*60,0)/(24*60) > fn[dad]:
            fn[dad]=max(C-jobDict['dd'+str(j)]*24*60,0)/(24*60)
    print (f"fitness of individual {dad} after cross over and mutaion: " + str(fn[dad]))
    C=0
    for j in pop[mom]:
        C+=jobDict['pt'+str(j)]
        if max(C-jobDict['dd'+str(j)]*24*60,0)/(24*60) > fn[mom]:
            fn[mom]=max(C-jobDict['dd'+str(j)]*24*60,0)/(24*60)
    print (f"fitness of individual {mom} after cross over and mutaion: " + str(fn[mom]))
    s=10000
    for s1 in fn:
        if fn[s1]<s:
            s=fn[s1]
    if s<i<z:
        z=s
    elif i<z:
        z=i
    print (f"the best outcome of Gen {g}: {s} days")
    print (f"the best outcome until Gen {g}: {z} days")
    g+=1

