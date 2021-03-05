# 这里实现第一个版本的域分界算法，先取5000条数据进行基本的处理
from single_function import hex_str_to_binary_str, choose_max, Single_Data, Classfy_Results
import pandas as pd
import numpy as np
from pandas import DataFrame
# 数据规格化使用了excel的筛选功能，需要后续提高代码的适用性
# 现在已经基本写完了域分界算法，下面对数据进行合理的分类操作，从而提高运行的速度哦

data_list = []
data_length = 0


classfy_results_list = []
# 首先读入数据


Path = "./source/origin_source/C9_data.xlsx"

# 在这里仅仅获取5000行数据，从而提高运行的效率
# C1_data = pd.read_excel(Path, encoding='utf-8', nrows=1000)
C1_data = pd.read_excel(Path, encoding='utf-8')
print(C1_data.head(5))

for index, row in C1_data.iterrows():
    tmp = Single_Data()
    tmp.can_id = row['can_id']
    tmp.time = row['time']
    tmp_str_data = ""
    for i in range(0, 8):
        in_index = 'data' + str(i)
        tmp_single_str = str(row[in_index])
        if len(tmp_single_str) == 1:
            tmp_single_str = '0' + tmp_single_str
        # 这里居然也是str  我直接震惊了
        tmp_str_data = tmp_str_data + tmp_single_str
    tmp.data_in_hex = tmp_str_data

    # 一番操作完成了基本的异常处理代码
    # !  这里字符串的长度需要规格化，缺少相关的异常处理代码 !!
    tmp.data_in_binary = hex_str_to_binary_str(tmp_str_data)
    data_list.append(tmp)
print(len(data_list))
# 得到了底层的数据结构，为接下来的操作打下了基础
# 也就是这里的data是64bits的数据

# 在这里指出二进制的位数，为下文的矩阵打下了基础
# 谨记是左三角矩阵
data_length = 64

classfy_matrix = np.zeros((data_length, data_length))
print(classfy_matrix[0][0])

# 矩阵的坐标从0开始  字符串坐标也从0开始
for i in range(0, data_length):
    for j in range(0, data_length-i):
        classfy_matrix[i][j] = 1
# 赋值为1，代表这个点需要进行考虑

for i in range(0, data_length):
    for j in range(0, data_length-i):
        tmp_classfy_data = Classfy_Results()
        tmp_classfy_data.classfy_begin_loc = i
        tmp_classfy_data.classfy_length = j+1
        classfy_results_list.append(tmp_classfy_data)

# 先根据坐标存入所有分类信息，为下面的遍历做好准备
for classfy_result in classfy_results_list:
    # 在这里进行关于数据的处理过程，需要用到哈希表
    s = set([])
    begin_loc = classfy_result.classfy_begin_loc
    end_loc = classfy_result.classfy_length + begin_loc - 1

    for data in data_list:
        # print(data.data_in_binary[begin_loc:end_loc])
        # !! 这里的下标居然出现了问题，非常的隐蔽，非常隐蔽的错误
        s.add(data.data_in_binary[begin_loc:end_loc+1])
        # print(len(data.data_in_binary))

    # 则最后完成了统计数据的统计过程，在一定程度上提高了程序运行的效率
    # 顺便完成基本的分类算是比较好的
    length = end_loc - begin_loc + 1
    # 至此应当是完全复现了论文的内容了吧
    if len(s) == 1:
        # classfy_result.classfy_class = "const"
        classfy_result.classfy_class = 0
        classfy_result.classfy_score = length
        # 我去，这里的数据非常的灵敏，容易出现各种意外
    # 这里的数据是什么意思？感觉非常的混乱的，我直接裂开了
    # 首先消除定值的影响，之后再进行后续的处理，处理思路应当是正确的
    # 可能是某些地方的算法有问题的
    # elif len(s) <= min(((2**(0.5*length))), 12):
    elif len(s) <= 32:
        # classfy_result.classfy_class = "multi-value"
        classfy_result.classfy_class = 1
        classfy_result.classfy_score = length
    else:
        # classfy_result.classfy_class = "sensor or counter"
        # 以下是score的计算方法
        classfy_result.classfy_class = 2
        classfy_result.classfy_score = (len(s)*len(s)/2**length)
        # classfy_result.classfy_score = (len(s) / 2 ** length)

    print(str(classfy_result.classfy_begin_loc)+ " " +
          str(end_loc) + " " + str(classfy_result.classfy_class) + \
          " " + str(classfy_result.classfy_score) + " ")


# 以上代码完成了基本的分类，下面要进行贪心算法来进行复杂的操作，从而得出最佳的分类
const_class = None
multi_value_class = None
sensor_counter_class = None

loc = 0
final_res = []
available_set_section = set([])
available_set_section.add((0, 63))

'''
def choose_max(s1, s2, s3):
    # 这里的choose_max逻辑有问题？
    # 优先级的选择方式是不好确定的
    
    if s1 is None:
        if s2 is None:
            if s3 is None:
                return None
            else:
                return s3
        else:
            return s2
    else:
        return s1

    
    if s1 is None:
        if s2 is None:
            if s3 is None:
                return None
            else:
                return s3
        else:
            if s3 is None:
                return s2
            else:
                if s2.classfy_score > s3.classfy_score:
                    return s2
                else:
                    return s3
    else:
        if s2 is None:
            if s3 is None:
                return s1
            else:
                if s1.classfy_score>s3.classfy_score:
                    return s1
                else:
                    return s3
        else:
            if s3 is None:
                if s1.classfy_score > s2.classfy_score:
                    return s1
                else:
                    return s2


    if s1.classfy_score > s2.classfy_score:
        if s1.classfy_score > s3.classfy_score:
            return s1
        else:
            return s3
    elif s2.classfy_score > s3.classfy_score:
        return s2
    else:
        return s3
'''


# 一些细节的边界条件有问题
# 首先采用的是固定边界的const分界方法，事实证明这种方法准确度不太行，需要采用别的算法

# 需要对区间进行复杂的操作的
while len(available_set_section)!=0:
    # 这里存在一部分不定值的变化，在某种程度上是比较合理的
    for section in available_set_section:
        # print(str(section[0]) + " " + str(section[1]))
        begin_loc = section[0]
        length = section[1] - section[0] + 1
        end_loc = section[1]

        for classfy_result in classfy_results_list:
            # 这里的逻辑居然是有问题的，这属于编程失误
            if classfy_result.classfy_begin_loc >= begin_loc and \
                classfy_result.classfy_length + classfy_result.classfy_begin_loc -1 <= end_loc:
                if classfy_result.classfy_class == 0:
                    if const_class is None:
                        const_class = classfy_result
                    else:
                        if const_class.classfy_score < classfy_result.classfy_score:
                            const_class = classfy_result
                elif classfy_result.classfy_class == 1:
                    if multi_value_class is None:
                        multi_value_class = classfy_result
                    else:
                        if multi_value_class.classfy_score < classfy_result.classfy_score:
                            multi_value_class = classfy_result
                elif classfy_result.classfy_class == 2:
                    if sensor_counter_class is None:
                        sensor_counter_class = classfy_result
                    else:
                        if sensor_counter_class.classfy_score < classfy_result.classfy_score:
                            sensor_counter_class = classfy_result
    if const_class is not None:
        print("const: " + "begin: "+ str(const_class.classfy_begin_loc) + " length: " + str(const_class.classfy_length) + " score: " + str(const_class.classfy_score))
    if multi_value_class is not None:
        print("multi-value: " + "begin: "+ str(multi_value_class.classfy_begin_loc) + " length: " + str(multi_value_class.classfy_length) + " score: " + str(multi_value_class.classfy_score))
    if sensor_counter_class is not None:
        print("sensor-counter: " + "begin: "+ str(sensor_counter_class.classfy_begin_loc) + " length: " + str(sensor_counter_class.classfy_length) + " score: " + str(sensor_counter_class.classfy_score))
    tmp_res = choose_max(const_class, multi_value_class, sensor_counter_class)
    loc = tmp_res.classfy_begin_loc + tmp_res.classfy_length
    final_res.append(tmp_res)
    print("i am happy:::  " + str(tmp_res.classfy_class))

    classfy_result = tmp_res
    #print(str(classfy_result.classfy_begin_loc) + " " + str(
    #    classfy_result.classfy_begin_loc + classfy_result.classfy_length - 1) + " " + str(
    #   classfy_result.classfy_class) + " " + str(classfy_result.classfy_score) + " ")
    const_class = None
    multi_value_class = None
    sensor_counter_class = None

    begin_loc = tmp_res.classfy_begin_loc
    l = tmp_res.classfy_length
    end_loc = begin_loc + l -1

    target_loc = []
    target_section = None
    target_b = None
    target_e = None
    # print("begin location: " + str(begin_loc))
    # print("end_loc: " + str(end_loc))
    for section in available_set_section:
        if section[1] < begin_loc:
            continue
        elif section[0] > end_loc:
            continue
        else:
            left_begin_loc = section[0]
            left_end_loc = begin_loc - 1
            right_begin_loc = end_loc + 1
            right_end_loc = section[1]

            target_b = section[0]
            target_e = section[1]

            if left_end_loc >= left_begin_loc:
                target_loc.append((left_begin_loc, left_end_loc))
            if right_end_loc >= right_begin_loc:
                target_loc.append((right_begin_loc, right_end_loc))
            break
    # if target_b is None:
        # print("some basic number is None")
    if target_b is not None and target_e is not None:
        available_set_section.remove((target_b, target_e))
    for item in target_loc:
        available_set_section.add(item)
    # print("length of 可行的区间 is" + str(len(available_set_section)))
    # for item in available_set_section:
        # print("some basic symbol " + str(item[0]) + " " + str(item[1]))


'''
while loc<data_length-1:
    for classfy_result in classfy_results_list:
        if loc == classfy_result.classfy_begin_loc:
            if classfy_result.classfy_class == 0:
                if const_class is None:
                    const_class = classfy_result
                else:
                    if const_class.classfy_score < classfy_result.classfy_score:
                        const_class=classfy_result
            elif classfy_result.classfy_class == 1:
                if multi_value_class is None:
                    multi_value_class = classfy_result
                else:
                    if multi_value_class.classfy_score < classfy_result.classfy_score:
                        multi_value_class = classfy_result
            else:
                if sensor_counter_class is None:
                    sensor_counter_class = classfy_result
                else:
                    if sensor_counter_class.classfy_score < classfy_result.classfy_score:
                        sensor_counter_class = classfy_result.classfy_score
    print(const_class)
    print(multi_value_class)
    print(sensor_counter_class)
    tmp_res = choose_max(const_class, multi_value_class, sensor_counter_class)
    loc = tmp_res.classfy_begin_loc + tmp_res.classfy_length
    final_res.append(tmp_res)
    classfy_result = tmp_res
    print(str(classfy_result.classfy_begin_loc)+ " " + str(classfy_result.classfy_begin_loc + classfy_result.classfy_length -1) + " " + str(classfy_result.classfy_class) + " " + str(classfy_result.classfy_score) + " ")
    const_class = None
    multi_value_class = None
    sensor_counter_class = None
'''


print(len(final_res))
for classfy_result in final_res:
    print(str(classfy_result.classfy_begin_loc)+ " " + \
          str(classfy_result.classfy_begin_loc + classfy_result.classfy_length -1) \
          + " " + str(classfy_result.classfy_class) + " " + str(classfy_result.classfy_score) + " ")
