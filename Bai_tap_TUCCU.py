import pandas as pd
import numpy as np
import random
import time
import plotly.graph_objects as go

# ==========================================
# CÁC HÀM HỖ TRỢ (Crossover, Mutation, Fitness, Selection)
# ==========================================
def crossover(Dad, Mom):
    size = len(Dad)
    p1, p2 = sorted(random.sample(range(size), 2))
    child1 = [None] * size
    child2 = [None] * size

    child1[p1:p2+1] = Dad[p1:p2+1]
    child2[p1:p2+1] = Mom[p1:p2+1]

    rem1 = [item for item in Mom if item not in child1]
    rem2 = [item for item in Dad if item not in child2]

    idx1, idx2 = 0, 0
    for i in range(size):
        if child1[i] is None:
            child1[i] = rem1[idx1]
            idx1 += 1
        if child2[i] is None:
            child2[i] = rem2[idx2]
            idx2 += 1

    return child1, child2, p1, p2

def mutation(child):
    child_mutated = child.copy()
    size = len(child)
    p1, p2 = sorted(random.sample(range(size), 2))
    child_mutated[p1], child_mutated[p2] = child_mutated[p2], child_mutated[p1]
    return child_mutated, p1, p2

def calculate_fitness(individual, jobDict):
    C = 0
    max_lateness = 0
    for j in individual:
        if C <= jobDict['rd' + str(j)]:
            C = jobDict['rd' + str(j)] + jobDict['pt' + str(j)]
        else:
            C += jobDict['pt' + str(j)]
        lateness = max(C - jobDict['dd' + str(j)] * 24 * 60, 0) / (24 * 60)
        if lateness > max_lateness:
            max_lateness = lateness
    return max_lateness

def roulette_wheel_selection(fn_dict):
    """
    Chọn lọc một cá thể dựa trên Roulette Wheel Selection.
    Vì L_max nhỏ là tốt, ta dùng nghịch đảo: score = 1 / (1 + l_max)
    """
    draft_inv_fitness = {k: 1.0 / (1.0 + v) for k, v in fn_dict.items()} ##Key: k, value: 1/(1+v) | k,v chạy trong dict fn_dict
    inv_fitness = sorted(draft_inv_fitness.items(), key=lambda item: item[1]) #sắp sếp lại dict với các key k ứng với value tăng dần
    total_fit = sum(val for _, val in inv_fitness) ##Tính tổng fitness

    current = 0
    cumulative_probs = []
    for k, fit in inv_fitness:
        current += fit / total_fit
        cumulative_probs.append((k, current))

    #Bắt đầu quay roulette
    r = random.random() ##Sinh ra một số thực ngẫu nhiên r nằm trong đoạn [0, 1]
    for k, cp in cumulative_probs:
        if r <= cp:
            return k
    return cumulative_probs[-1][0] ##lỡ trường hợp r >cp (do cộng sai số dẫn đến lớn hơn 1) thì sẽ trả ra giá trị cặp k:value cuối, lấy k cuối


# ==========================================
# 1. Nhập tham số & Khởi tạo quần thể độc lập
# ==========================================
r = int(input("Please enter the desired number of generations: "))
s = int(input("Please enter the desired number of population: "))

print ("Nhớ update lại pm, pc")
time.sleep(3)
pc=0.8
pm=0.2
"""
while True:
    pc = float(input("Please enter the crossover rate (0 to 1): "))
    if 0 <= pc <= 1 and isinstance(pc, float):
        break
    else:
        print("Invalid, please try again!")

while True:
    pm = float(input("Please enter the mutation rate (0 to 1): "))
    if 0 <= pm <= 1 and isinstance(pm, float):
        break
    else:
        print("Invalid, please try again!")
"""
x = input("Enter the total jobs: ")

# Khởi tạo quần thể không trùng lặp
pop = {}
seen_chromosomes = set()
total_jobs = int(x)

while len(pop) < s:
    chrom = [str(num) for num in random.sample(range(1, total_jobs + 1), total_jobs)]
    chrom_tuple = tuple(chrom)

    if chrom_tuple not in seen_chromosomes:
        seen_chromosomes.add(chrom_tuple)
        pop[len(pop) + 1] = chrom

# In thử kết quả quần thể ban đầu
for key in pop:
    print(f"individual {key}: {pop[key]}\n")


# ==========================================
# 2. Nhập đường dẫn file và chọn Sheet
# ==========================================
file_path = r"C:\Users\My Pc\Downloads\D019AE30.xlsx"
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
# 3. Xử lý dữ liệu công việc & Tính Fitness ban đầu
# ==========================================
jobDict = {}
for job, pt, dd, rd in zip(df['job'], df['processing_time'], df['Due_date'], df['ready_date']):
    if ('pt' + str(job)) not in jobDict:
        jobDict['pt' + str(job)] = pt
    else:
        jobDict['pt' + str(job)] += pt
    if ('dd' + str(job)) not in jobDict:
        jobDict['dd' + str(job)] = dd
    else:
        jobDict['dd' + str(job)] += dd
    if ('rd' + str(job)) not in jobDict:
        jobDict['rd' + str(job)] = rd

print(jobDict)

fn = {}
for k in pop:
    fn[k] = calculate_fitness(pop[k], jobDict)
    print(f"fitness of individual {k}: {fn[k]}")
#===========Pause để kiểm tra thông số===========
while True:
    pause =input ("nhập 'x' để tiếp tục")
    if pause == 'x':
        break


# ==========================================
# 4. Vòng lặp tiến hóa (Evolutionary Loop)
# ==========================================
g = 1
z = float('inf') # Kỷ lục tốt nhất toàn cục
draw_list=[]
while g <= r:
    print(f"\n===== GEN {g} =====")

    # 1. Lưu lại 4 cá thể tinh hoa đời cũ (Elitism) trước khi tiến hành lai ghép đột biến hàng loạt
    sorted_pop_old = sorted(fn.items(), key=lambda item: item[1])
    top_elites = []
    for best_id, best_fit in sorted_pop_old[:min(4, len(sorted_pop_old))]:
        top_elites.append({
            'id': best_id,
            'chrom': pop[best_id].copy(),
            'fitness': best_fit
        })

    # 2. Thực hiện liên tục đủ 50 cặp Crossover & Mutation trong thế hệ này
    num_pairs = 50
    print(f"Starting evolutionary operations for {num_pairs} pairs in Gen {g}...")

    for pair_idx in range(1, num_pairs + 1):
        # Chọn Dad và Mom bằng Roulette Wheel Selection
        dad = roulette_wheel_selection(fn)
        mom = roulette_wheel_selection(fn)
        while mom == dad and len(pop) > 1:
            mom = roulette_wheel_selection(fn)

        # Lai ghép (Crossover) nếu số thực random [0, 1] <= pc
        r_crossover = random.random()
        if r_crossover <= pc:
            pop[dad], pop[mom], _, _ = crossover(pop[dad], pop[mom]) #gán child 1, child 2 của def crossover cho dad, mom luôn. Skip 2 điểm cắt

        # Đột biến (Mutation) cho Dad nếu số thực random [0, 1] <= pm
        r_mutation_dad = random.random()
        if r_mutation_dad <= pm:
            pop[dad], _, _ = mutation(pop[dad]) #gán mutation child cho dad luôn, skip 2 điểm cắt

        # Đột biến (Mutation) cho Mom nếu số thực random [0, 1] <= pm
        r_mutation_mom = random.random()
        if r_mutation_mom <= pm:
            pop[mom], _, _ = mutation(pop[mom]) #gán mutation child cho mom luôn, skip 2 điểm cắt

        # Cập nhật lại Fitness cho Dad và Mom vào bộ dữ liệu
        fn[dad] = calculate_fitness(pop[dad], jobDict)
        fn[mom] = calculate_fitness(pop[mom], jobDict)

    print(f"Completed {num_pairs} pairs of crossover and mutation operations.")

    # 3. Áp dụng Elitism: Giữ lại 4 cá thể tốt nhất đời cũ đè lên 4 cá thể tệ nhất sau 50 vòng tiến hóa
    sorted_pop_new = sorted(fn.items(), key=lambda item: item[1])
    num_elites = len(top_elites)
    worst_ids = [item[0] for item in sorted_pop_new[-num_elites:]]

    for idx, elite in enumerate(top_elites):
        worst_id = worst_ids[idx]
        if elite['fitness'] < fn[worst_id]:
            pop[worst_id] = elite['chrom']
            fn[worst_id] = elite['fitness']
            print(f"Elitism applied: Restored elite {elite['id']} (fit={elite['fitness']}) into worst id {worst_id}")

    # 4. Thống kê kết quả thế hệ
    s = min(fn.values())
    if s < z:
        z = s

    print(f"the best outcome of Gen {g}: {s} days")
    print(f"the best outcome until Gen {g}: {z} days")
    draw_list.append(s)
    g += 1
# ==========================================
# 5. In kết quả tốt nhất cuối cùng
# ==========================================
best_overall_id = min(fn, key=fn.get)
print(f"\n==========================================")
print(f"BEST OVERALL RESULT:")
print(f"Chromosome (Job Order): {pop[best_overall_id]}")
print(f"Maximum Lateness (L_max): {fn[best_overall_id]} days")
print(f"==========================================")
time.sleep(3)
# ==========================================
# 6. vẽ biểu đồ
# ==========================================
while True:
    pause =input ("nhập 'x' để tiếp tục")
    if pause == 'x':
        break

x_list=list(range(1, len(draw_list) + 1))
y_list =draw_list
line_chart=go.Scatter(
x=x_list,
y=y_list,
mode='lines',
line=dict(
color='#1f77b4',
width=1.5
),
name='Max lateness'
)
chart=go.Layout(
title=dict(
text='Biểu đồ Độ trễ tốt nhất qua mỗi gen',
font=dict(size=18, family='Arial', color='black')
),
xaxis=dict(
        title='Gen',
        tickangle=45,
        showgrid=True
    ),
yaxis=dict(
        title='Late_ness (days)',
        range=[0, 7],
        showgrid=True
    ),
   margin=dict(l=50, r=50, t=80, b=50),
    hovermode='x unified'
)
fig = go.Figure(data=[line_chart], layout=chart)
fig.show()
