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
    WLateness = 0
    # List lưu thời gian rảnh của 11 chuyền
    line = [0] * 11
    # List lưu job cuối cùng đã chạy trên từng chuyền tương ứng (ban đầu là None)
    line_last_job = [None] * 11
    for j in individual:
        # Tìm chuyền sớm nhất available
        min_line = min(line)
        min_index = line.index(min_line) # xác định chuyền được chọn là chuyền thứ mấy

        # Xác định thời gian chuyển đổi
        prevCr = line_last_job[min_index]
        tt = 0
        if prevCr is not None:
            if jobDict['fm' + str(prevCr)] != jobDict['fm' + str(j)]:
                tt = 10752  # 1 ngày làm việc
            elif jobDict['st' + str(prevCr)] != jobDict['st' + str(j)]:
                tt = 10752 * 0.2 #0.2 ngày làm việc
            else:
                tt = 5 # 5 phút

        #Xác định chuyền ready, NVL ready
        C=max(min_line, jobDict['rd' + str(j)]*10752) #tính theo phút (1 ngày 1 chuyền chỉ chạy 10752 phút)

        #Cộng thêm processing time và thời gian chuyển đổi
        C = C + jobDict['pt' + str(j)] +tt

        #Update tg ready của chuyền đó và job cuối cùng đã chạy
        line[min_index] = C
        line_last_job[min_index] = j
        #tính độ trễ có trọng số
        lateness = max(C - jobDict['dd' + str(j)] * 10752, 0) / 10752 #Đơn vị (ngày)
        WLateness += lateness * jobDict['wei' + str(j)]
    return WLateness  # Trả kết quả tổng độ trễ có trọng số

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


while True:
    pc = float(input("Please enter the crossover rate (0 to 1): "))
    if 0 <= pc <= 1:
        break
    else:
        print("Invalid, please try again!")

while True:
    pm = float(input("Please enter the mutation rate (0 to 1): "))
    if 0 <= pm <= 1:
        break
    else:
        print("Invalid, please try again!")

x = input("Enter the total jobs: ")

# Khởi tạo quần thể không trùng lặp
pop = {}
seen_chromosomes = set()
total_jobs = int(x)

while len(pop) < s-1:
    chrom = [str(num) for num in random.sample(range(1, total_jobs + 1), total_jobs)]
    chrom_tuple = tuple(chrom)

    if chrom_tuple not in seen_chromosomes:
        seen_chromosomes.add(chrom_tuple)
        pop[len(pop) + 1] = chrom

#Gán cá thể cuối cùng trong quần thể bằng kết quả của 1 giải thuật đơn giản Weighted Earliest Due date
pop[s]= ['8', '11', '3', '2', '7', '1', '6', '10', '5', '4', '9', '19', '21', '18', '25', '26', '22', '13', '17', '15', '24', '16', '20', '12', '23', '14', '28', '29', '31', '32', '33', '30', '27', '38', '34', '40', '35', '39', '37', '50', '36', '45', '47', '46', '49', '43', '42', '41', '44', '48', '54', '51', '53', '52', '56', '55', '59', '57', '61', '63', '58', '62', '60', '64', '65', '69', '68', '66', '71', '70', '67', '72', '73', '74', '87', '76', '80', '83', '75', '86', '81', '79', '84', '77', '85', '82', '78', '88', '89', '90', '98', '100', '94', '99', '95', '96', '97', '101', '91', '93', '92', '102', '103', '104', '111', '112', '109', '110', '108', '105', '107', '106', '115', '116', '113', '114', '117', '118', '124', '130', '172', '123', '131', '126', '120', '119', '128', '125', '127', '121', '122', '129', '133', '134', '132', '135', '142', '143', '138', '136', '140', '144', '146', '137', '141', '139', '145', '147', '148', '151', '157', '154', '150', '155', '149', '153', '156', '152', '158', '160', '159', '162', '161', '164', '165', '166', '168', '167', '163', '169', '171', '170']

# In thử kết quả quần thể ban đầu
for key in pop:
    print(f"individual {key}: {pop[key]}\n")


# ==========================================
# 2. Nhập đường dẫn file và chọn Sheet
# ==========================================
file_path = r"C:\Users\admin\Downloads\data bài toán.xlsx"
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
for job, pt, dd, rd, fm, st, clr, wei in zip(df['job'], df['processing_time (minutes)'], df['Due_date'],
df['Ready_date'], df['category'], df['STYLE'], df['COLOR'], df['Weighted average (percentage)']):
    if ('pt' + str(job)) not in jobDict:
        jobDict['pt' + str(job)] = pt
    else:
        jobDict['pt' + str(job)] += pt
    if ('dd' + str(job)) not in jobDict:
        jobDict['dd' + str(job)] = dd
    if ('rd' + str(job)) not in jobDict:
        jobDict['rd' + str(job)] = rd
    if ('fm' + str(job)) not in jobDict:
        jobDict['fm' + str(job)] = fm
    if ('st' + str(job)) not in jobDict:
        jobDict['st' + str(job)] = st
    if ('clr' + str(job)) not in jobDict:
        jobDict['clr' + str(job)] = 1
        # tính số màu trong mỗi job để biết transition time
    else:
        jobDict['clr' + str(job)] += 1
        jobDict['pt' + str(job)] += 25
    if ('wei' + str(job)) not in jobDict:
        jobDict['wei' + str(job)] = wei
    else:
        jobDict['wei' + str(job)] += wei

# Lọc ra danh sách các job độc lập từ jobDict dựa vào các key bắt đầu bằng 'pt'
job_ids = [k.replace('pt', '') for k in jobDict.keys() if k.startswith('pt')]

for j in job_ids:
    print(f"--- Job ID: {j} ---")
    print(f"  Processing Time : {jobDict.get('pt' + j)}")
    print(f"  Due Date        : {jobDict.get('dd' + j)}")
    print(f"  Ready Date      : {jobDict.get('rd' + j)}")
    print(f"  Category        : {jobDict.get('fm' + j)}")
    print(f"  Style           : {jobDict.get('st' + j)}")
    print(f"  Color           : {jobDict.get('clr' + j)}")
    print(f"  Weighted Average: {jobDict.get('wei' + j)}")
    print("-" * 30)

fn = {}
for k in pop:
    fn[k] = calculate_fitness(pop[k], jobDict)
    print(f"fitness of individual {k}: {fn[k]}")
#===========Pause để kiểm tra thông số===========
while True:
    print ("Vui lòng kiểm tra lại Job dictionary và fitness từng cá thể")
    pause =input ("Nhập 'x' để tiếp tục")
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

    # 1. Lưu lại 4 cá thể tinh hoa (Elitism) từ đời cũ
    sorted_pop_old = sorted(fn.items(), key=lambda item: item[1])
    top_elites = []
    for best_id, best_fit in sorted_pop_old[:min(4, len(sorted_pop_old))]:
        top_elites.append({
            'chrom': pop[best_id].copy(),
            'fitness': best_fit
        })

    # 2. Khởi tạo quần thể mới (new_pop) và đưa thẳng 4 cá thể tinh hoa vào ngay từ đầu
    new_pop = {}
    for idx, elite in enumerate(top_elites, start=1):
        new_pop[idx] = elite['chrom'].copy()

    # 3. Thực hiện sinh thêm (s - 4) cá thể con thông qua lai ghép và đột biến
    num_pairs = int((s - 4) / 2)
    print(f"Starting evolutionary operations for {num_pairs} pairs in Gen {g}...")

    for pair_idx in range(1, num_pairs + 1):
        # Chọn Dad và Mom từ quần thể cũ (pop) bằng Roulette Wheel Selection
        dad = roulette_wheel_selection(fn)
        mom = roulette_wheel_selection(fn)
        while mom == dad and len(pop) > 1:
            mom = roulette_wheel_selection(fn)

        # Lấy bản sao của bố và mẹ để lai ghép, bảo vệ quần thể cũ
        child1 = pop[dad].copy()
        child2 = pop[mom].copy()

        # Lai ghép (Crossover) nếu số thực random [0, 1] <= pc
        if random.random() <= pc:
            child1, child2, _, _ = crossover(child1, child2)

        # Đột biến (Mutation) cho Child 1 nếu số thực random [0, 1] <= pm
        if random.random() <= pm:
            child1, _, _ = mutation(child1)

        # Đột biến (Mutation) cho Child 2 nếu số thực random [0, 1] <= pm
        if random.random() <= pm:
            child2, _, _ = mutation(child2)

        # Thêm các con mới vào new_pop sao cho không vượt quá kích thước s
        next_id = len(new_pop) + 1
        new_pop[next_id] = child1
        if len(new_pop) < s:
            next_id_2 = len(new_pop) + 1
            new_pop[next_id_2] = child2

    print(f"Completed crossover and mutation operations for Gen {g}.")

    # 4. Cập nhật lại pop thành new_pop và tính toán lại bảng fitness (fn) cho thế hệ mới
    pop = new_pop.copy()
    fn = {}
    for k in pop:
        fn[k] = calculate_fitness(pop[k], jobDict)

    # 5. Thống kê kết quả thế hệ
    ss = min(fn.values())
    if ss < z:
        z = ss

    print(f"the best outcome of Gen {g}: {ss} days - W.Avrg")
    print(f"the best outcome until Gen {g}: {z} days - W.Avrg")
    draw_list.append(ss)
    g += 1
# ==========================================
# 5. In kết quả tốt nhất cuối cùng
# ==========================================
best_overall_id = min(fn, key=fn.get)
print(f"\n==========================================")
print(f"BEST OVERALL RESULT:")
print(f"Chromosome (Job Order): {pop[best_overall_id]}")
print(f"Maximum Weighted Lateness: {fn[best_overall_id]} days - W.Avrg")
print(f"==========================================")
time.sleep(3)
# ==========================================
# 6. vẽ biểu đồ
# ==========================================
while True:
    pause =input ("nhập 'x' để tiếp tục vẽ biểu đồ: ")
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
name='Tổng độ trễ có trọng số'
)
chart=go.Layout(
title=dict(
text='Biểu đồ giá trị tốt nhất qua mỗi gen',
font=dict(size=18, family='Arial', color='black')
),
xaxis=dict(
        title='Gen',
        tickangle=45,
        showgrid=True
    ),
yaxis=dict(
        title='Total W.Late_ness (days - W.AVRG)',
        range=[0, 3],
        showgrid=True
    ),
   margin=dict(l=50, r=50, t=80, b=50),
    hovermode='x unified'
)
fig = go.Figure(data=[line_chart], layout=chart)
fig.show()

# ==========================================
# BỔ SUNG: Thống kê Job trễ & Biểu đồ Gantt 11 chuyền
# ==========================================

while True:
    pause =input ("nhập 'x' để xem số ngày trễ mõi Job: ")
    if pause == 'x':
        break

import plotly.express as px

# 1. Mô phỏng lại tiến trình chạy của chuỗi nhiễm sắc thể tốt nhất để lấy lịch trình chi tiết từng chuyền
best_individual = pop[best_overall_id]
line_schedule = [] # Lưu thông tin các task chạy trên từng chuyền để vẽ Gantt
line_times = [0] * 11
line_last_job = [None] * 11
delayed_jobs_info = []

for j in best_individual:
    min_line = min(line_times)
    min_index = line_times.index(min_line)

    prevCr = line_last_job[min_index]
    tt = 0
    if prevCr is not None:
        if jobDict['fm' + str(prevCr)] != jobDict['fm' + str(j)]:
            tt = 10752
        elif jobDict['st' + str(prevCr)] != jobDict['st' + str(j)]:
            tt = 10752 * 0.2
        else:
            tt = 5

    start_time = max(min_line, jobDict['rd' + str(j)] * 10752)
    start_time += tt
    end_time = start_time + jobDict['pt' + str(j)]

    # Cập nhật thời gian rảnh của chuyền
    line_times[min_index] = end_time
    line_last_job[min_index] = j

    # Tính độ trễ (đơn vị: ngày)
    due_date_mins = jobDict['dd' + str(j)] * 10752
    lateness_days = max((end_time - due_date_mins) / 10752, 0)

    if lateness_days > 0:
        delayed_jobs_info.append({
            'Job': j,
            'Line': f"Chuyền {min_index + 1}",
            'Lateness_Days': lateness_days,
            'End_Time_Days': end_time / 10752,
            'Due_Date_Days': jobDict['dd' + str(j)]
        })

    # Lưu lại để vẽ Gantt (quy đổi thời gian ra ngày cho dễ nhìn trên biểu đồ)
    line_schedule.append(dict(
        Job=f"Job {j}",
        Line=f"Chuyền {min_index + 1}",
        Start=start_time / 10752,
        Finish=end_time / 10752,
        Category=jobDict['fm' + str(j)]
    ))

# In tổng kết các job bị trễ vào phần kết quả cuối
print(f"\n==========================================")
print(f"THỐNG KÊ CÁC JOB BỊ TRỄ HẠN:")
if len(delayed_jobs_info) > 0:
    print(f"Tổng số job bị trễ: {len(delayed_jobs_info)} job")
    for item in delayed_jobs_info:
        print(f" - Job {item['Job']} (Chạy trên {item['Line']}): Trễ {item['Lateness_Days']:.2f} ngày (Hoàn thành ngày {item['End_Time_Days']:.2f}, Due date: {item['Due_Date_Days']})")
else:
    print("Chúc mừng! Không có job nào bị trễ hạn.")
print(f"==========================================")

# Vẽ biểu đồ Gantt cho 11 chuyền bằng plotly.graph_objects

while True:
    pause =input ("nhập 'x' để xem biểu đồ Gant mỗi chuyền: ")
    if pause == 'x':
        break

import plotly.graph_objects as go

gantt_fig = go.Figure()

# 1. Màu sắc phân biệt theo Category/Family
color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
categories = list(set([item['Category'] for item in line_schedule]))
cat_color_map = {cat: color_palette[i % len(color_palette)] for i, cat in enumerate(categories)}

# Theo dõi các category đã đưa vào legend để tránh bị lặp tên quá nhiều lần trên chú thích
legend_added = set()

# 2. Thêm từng task (Job) vào biểu đồ
for task in line_schedule:
    cat = task['Category']
    # Chỉ hiển thị tên category lên legend 1 lần duy nhất cho gọn
    show_legend = False
    if cat not in legend_added:
        legend_added.add(cat)
        show_legend = True

    gantt_fig.add_trace(go.Bar(
        x=[task['Finish'] - task['Start']],  # Độ dài thời gian thực hiện job (Duration)
        y=[task['Line']],                    # Tên chuyền nằm trên trục Y
        base=[task['Start']],                # Ngày bắt đầu (Start time)
        orientation='h',                     # Thanh ngang (Gantt style)
        name=str(cat),                       # Gom nhóm màu theo Category trên Legend
        legendgroup=str(cat),
        showlegend=show_legend,
        text=task['Job'],                    # Hiển thị tên Job trực tiếp lên thanh bar
        textposition='inside',
        marker=dict(color=cat_color_map.get(cat, '#1f77b4')),
        hovertemplate=(
            f"<b>{task['Job']}</b><br>"
            f"Chuyền: {task['Line']}<br>"
            f"Thể loại: {cat}<br>"
            f"Bắt đầu: Ngày %{{base:.2f}}<br>"
            f"Kết thúc: Ngày %{{customdata:.2f}}<br>"
            f"Thời gian chạy: %{{x:.2f}} ngày<extra></extra>"
        ),
        customdata=[task['Finish']]
    ))

# 3. Cấu hình giao diện Layout cho 11 chuyền
gantt_fig.update_layout(
    title='<b>Biểu đồ Gantt Lịch trình Sản xuất 11 Chuyền</b>',
    xaxis_title='<b>Thời gian (Ngày)</b>',
    yaxis_title='<b>Chuyền sản xuất</b>',
    barmode='overlay',  # Dùng overlay để các job tuần tự trên cùng một chuyền không bị ép chồng lên nhau
    # Sắp xếp trục Y từ Chuyền 1 ở trên cùng đến Chuyền 11 ở dưới cùng
    yaxis=dict(
        categoryorder='array',
        categoryarray=[f"Chuyền {i}" for i in range(11, 0, -1)], # Đảo ngược để Chuyền 1 hiện lên trên đỉnh
        showgrid=True
    ),
    xaxis=dict(
        showgrid=True,
        zeroline=False
    ),
    template='plotly_white',
    hovermode='closest',
    margin=dict(l=100, r=50, t=80, b=50),
    height=600  # Đảm bảo chiều cao đủ thoáng cho 11 hàng ngang
)

gantt_fig.show()
