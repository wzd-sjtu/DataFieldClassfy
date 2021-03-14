# 本文件用于读取数据
from used_class import hex_str_to_binary_str, \
    choose_max, Single_Data, \
    Classfy_Results, choose_max_plus
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


path = ".././source/origin_source/data.csv"
write_path = ".././source/origin_source/result.csv"
nrows = 1000000


# 感觉并没有封装的作用，搞得人十分迷惑
# 如何利用面向对象提高程序运行效率？暂时是未知的
class Data():

    # 下面是几个类别的名字和数值对照表
    const_tag = 0
    multi_value_tag = 1
    sensor_or_counter_tag = 2

    counter_tag = 2
    sensor_tag = 3
    no_meaning_tag = 4
    def __init__(self):
        self.all_data = pd.read_csv(path,  nrows=nrows)
        self.CANID_set = set(self.all_data['can_id'])
        self.result_dict = {}
        self.result_dict['can_id']=[]
        self.result_dict['start_bit']=[]
        self.result_dict['end_bit']=[]
        self.result_dict['type']=[]
        self.result_dict['value_range'] = []
    # 处理所有数据集的过程
    def classfing_all_data(self):
        numbers = 0
        for can_id in self.CANID_set:
            self.can_id = can_id
            self.origin_data = self.all_data.loc[self.all_data["can_id"] == can_id]
            self.reset()
            self.store_data_with_can_matrix()
            self.set_data_length()

            # 进行分类
            self.initial_classfy_data()
            self.process_classfy_data()

            # 贪心算法求最优解
            self.greedy_find_solution()

            # 显示
            self.save_results()
            print("number is" + str(numbers) + can_id)
            numbers = numbers + 1
        self.result_dataframe = pd.DataFrame(data = self.result_dict,columns=['can_id','start_bit','end_bit','type','value_range'])
        self.result_dataframe.to_csv(write_path,index=False,sep=',')
    # 处理单个数据集的过程
    def classfying_single_data(self,path, nrows):
        self.reset()
        self.store_data_with_can_matrix_for_single_canid(path, nrows)
        self.set_data_length()

        # 进行分类
        self.initial_classfy_data()
        self.process_classfy_data()

        # 贪心算法求最优解
        self.greedy_find_solution()

        # 显示
        self.show_results()
    # 每一次reset都会进行复杂的操作的
    # 下面给出基本的代码
    def reset(self):
        # 源数据的位置就是在这里的
        self.data_list = []
        self.data_length = 0
        # classfy_results_list是分好类的数据
        self.classfy_results_list = []

        # 用于存储每一轮迭代中每种类别的最优解
        self.const_class = None
        self.multi_value_class = None
        self.sensor_counter_class = None
        # 加入两个新的类
        self.sensor_class = None
        self.counter_class = None
        # no_meaning_class 是不进行处理的类？直接忽略这里的影响了
        self.no_meaning_class = None

        self.loc = 0
        self.final_res = []
        self.available_set_section = set([])


    # 读取带有通信矩阵的数据
    def store_data_with_can_matrix(self):
        # 构建基础整理数据
        for index, row in self.origin_data.iterrows():
            tmp = Single_Data()
            tmp.can_id = row['can_id']
            tmp.time = row['time']
            tmp_str_data = ""
            for i in range(0, row['length']):
                in_index = 'data' + str(i)
                tmp_single_str = str(row[in_index])
                if len(tmp_single_str) == 1:
                    tmp_single_str = '0' + tmp_single_str
                tmp_str_data = tmp_str_data + tmp_single_str
            tmp.data_in_hex = tmp_str_data

            tmp.data_in_binary = hex_str_to_binary_str(tmp_str_data)
            self.data_list.append(tmp)

    # 读取带有通信矩阵的数据，存储仅仅有一个
    def store_data_with_can_matrix_for_single_canid(self, path, line_number):
        # self.origin_data = pd.read_excel(Path, encoding='utf-8', nrows=1000)
        self.origin_data = pd.read_excel(path, encoding='utf-8', nrows=line_number)
        print(self.origin_data.head(5))

        # 构建基础整理数据
        for index, row in self.origin_data.iterrows():
            tmp = Single_Data()
            tmp.can_id = row['can_id']
            tmp.time = row['time']
            tmp_str_data = ""
            for i in range(0, 8):
                in_index = 'data' + str(i)
                tmp_single_str = str(row[in_index])
                if len(tmp_single_str) == 1:
                    tmp_single_str = '0' + tmp_single_str
                tmp_str_data = tmp_str_data + tmp_single_str
            tmp.data_in_hex = tmp_str_data

            tmp.data_in_binary = hex_str_to_binary_str(tmp_str_data)
            self.data_list.append(tmp)
    # 应当先导入数据集，再设置数据字段长度
    # 应当先导入数据集，再设置数据字段长度
    # 数据字段的设置，给了程序多态性的特征，提高了程序的适用性
    def set_data_length(self):
        self.data_length = len(self.data_list[0].data_in_binary)
        return
    # 每一个分类都被存储，免去了后文考虑下标的问题
    def initial_classfy_data(self):
        for i in range(0, self.data_length):
            for j in range(0, self.data_length - i):
                tmp_classfy_data = Classfy_Results()
                tmp_classfy_data.classfy_begin_loc = i
                tmp_classfy_data.classfy_length = j + 1
                self.classfy_results_list.append(tmp_classfy_data)
        return
    # 处理分类数据，这里面有分类的详细标准
    def is_okay_with_counter(self, classfy_result):
        # 标志是否进入循环计数位

        pre_number = None
        diff_number = None
        begin_loc = classfy_result.classfy_begin_loc
        end_loc = classfy_result.classfy_length + begin_loc - 1
        length = end_loc - begin_loc + 1
        mod_number = 2**length

        for data in self.data_list:

            now_number = int(data.data_in_binary[begin_loc:end_loc + 1], 2)
            '''
            if begin_loc == 0 and end_loc == 1:
                print(now_number)
                print(pre_number)
                print(mod_number)
                print("above")
            '''
            if pre_number is not None and diff_number is not None:
                now_diff = (now_number + mod_number - pre_number) % mod_number
                if now_diff != diff_number:
                    # print("begin_loc " + str(begin_loc) + " end_loc " + str(end_loc) + " diff_number " + str(now_diff) + " pre_diff " + str(diff_number))
                    return False
                else:
                    pre_number = now_number
            elif pre_number is None:
                pre_number = now_number
            elif diff_number is None:
                diff_number = now_number - pre_number
                pre_number = now_number
        return True

    def process_classfy_data(self):
        for classfy_result in self.classfy_results_list:
            s = set([])
            begin_loc = classfy_result.classfy_begin_loc
            end_loc = classfy_result.classfy_length + begin_loc - 1

            # 在这里位置是双闭区间
            for data in self.data_list:
                s.add(data.data_in_binary[begin_loc:end_loc + 1])
            length = end_loc - begin_loc + 1

            # 以下的注释代表了许多种情况的
            if len(s) == 1:
                # classfy_result.classfy_class = "const"
                classfy_result.classfy_class = self.const_tag
                classfy_result.classfy_score = length

                # 这里默认是list存储数据范围
                # value_type是否有必要呢？貌似没有必要性
                # classfy_result.classfy_value_type = 0
                classfy_result.classfy_value_store = []
                for str_binary_value in s:
                    classfy_result.classfy_value_store.append(int(str_binary_value, 2))
            # 计数器的判断明显是有问题的
            elif self.is_okay_with_counter(classfy_result):

                classfy_result.classfy_class = self.counter_tag
                classfy_result.classfy_score = (len(s) * len(s) / 2 ** length)

                classfy_result.classfy_value_store = []
                middle_no_use_list = []
                for str_binary_value in s:
                    middle_no_use_list.append(int(str_binary_value, 2))
                # 计数器认为包含这个区间的
                classfy_result.classfy_value_store.append(min(middle_no_use_list))
                classfy_result.classfy_value_store.append(max(middle_no_use_list))

            # elif len(s) <= min(2**(0.5*length), 12):
            elif len(s) <= min(2**(0.5*length), 12) and length >= 3:
                # classfy_result.classfy_class = "multi-value"
                classfy_result.classfy_class = self.multi_value_tag
                classfy_result.classfy_score = length

                # classfy_result.classfy_value_type = 0
                classfy_result.classfy_value_store = []
                for str_binary_value in s:
                    classfy_result.classfy_value_store.append(int(str_binary_value, 2))

            elif length >= 3:
                # classfy_result.classfy_class = "sensor or counter"
                # 以下是score的计算方法

                #
                # 在这里是传感器？
                classfy_result.classfy_class = self.sensor_tag
                classfy_result.classfy_score = (len(s) * len(s) / 2 ** length)

                classfy_result.classfy_value_store = []
                middle_no_use_list = []
                for str_binary_value in s:
                    middle_no_use_list.append(int(str_binary_value, 2))

                classfy_result.classfy_value_store.append(min(middle_no_use_list))
                classfy_result.classfy_value_store.append(max(middle_no_use_list))

                # classfy_result.classfy_score = (len(s) / 2 ** length)
            else:
                # 第四类，可以直接忽略,直接忽略貌似有点不太严谨了
                classfy_result.classfy_class = self.no_meaning_tag
                classfy_result.classfy_score = length

                classfy_result.classfy_value_store = []
            '''
            # 打印所有的分类结果
            print(str(classfy_result.classfy_begin_loc) + " " +
                  str(end_loc) + " " + str(classfy_result.classfy_class) + \
                  " " + str(classfy_result.classfy_score) + " ")
            '''
        return

    def greedy_find_solution(self):
        self.available_set_section.add((0, self.data_length-1))
        while len(self.available_set_section) != 0:
            for section in self.available_set_section:
                begin_loc = section[0]
                length = section[1] - section[0] + 1
                end_loc = section[1]

                for classfy_result in self.classfy_results_list:
                    if classfy_result.classfy_begin_loc >= begin_loc and \
                            classfy_result.classfy_length + classfy_result.classfy_begin_loc - 1 <= end_loc:
                        if classfy_result.classfy_class == self.const_tag:
                            if self.const_class is None:
                                self.const_class = classfy_result
                            else:
                                if self.const_class.classfy_score < classfy_result.classfy_score:
                                    self.const_class = classfy_result
                        elif classfy_result.classfy_class == self.multi_value_tag:
                            if self.multi_value_class is None:
                                self.multi_value_class = classfy_result
                            else:
                                if self.multi_value_class.classfy_score < classfy_result.classfy_score:
                                    self.multi_value_class = classfy_result

                        elif classfy_result.classfy_class == self.counter_tag:
                            if self.counter_class is None:
                                self.counter_class = classfy_result
                            else:
                                if self.counter_class.classfy_score < classfy_result.classfy_score:
                                    self.counter_class = classfy_result

                        elif classfy_result.classfy_class == self.sensor_tag:
                            if self.sensor_class is None:
                                self.sensor_class = classfy_result
                            else:
                                if self.sensor_class.classfy_score < classfy_result.classfy_score:
                                    self.sensor_class = classfy_result

                        elif classfy_result.classfy_class == self.no_meaning_tag:
                            if self.no_meaning_class is None:
                                self.no_meaning_class = classfy_result
                            else:
                                if self.no_meaning_class.classfy_score < classfy_result.classfy_score:
                                    self.no_meaning_class = classfy_result
            '''
            if self.const_class is not None:
                print("const: " + "begin: " + str(self.const_class.classfy_begin_loc) + " length: " + str(
                    self.const_class.classfy_length) + " score: " + str(self.const_class.classfy_score))
            if self.multi_value_class is not None:
                print("multi-value: " + "begin: " + str(self.multi_value_class.classfy_begin_loc) + " length: " + str(
                    self.multi_value_class.classfy_length) + " score: " + str(self.multi_value_class.classfy_score))
            if self.sensor_counter_class is not None:
                print("sensor-counter: " + "begin: " + str(self.sensor_counter_class.classfy_begin_loc) + " length: " + str(
                    self.sensor_counter_class.classfy_length) + " score: " + str(self.sensor_counter_class.classfy_score))
            if self.no_meaning_class is not None:
                print("no_meaning_class: " + "begin: " + str(self.no_meaning_class.classfy_begin_loc) + " length: " + str(
                    self.no_meaning_class.classfy_length) + " score: " + str(self.no_meaning_class.classfy_score))

            '''
            # 选择最优解的关键函数
            # tmp_res = choose_max(self.const_class, self.multi_value_class, self.sensor_counter_class, self.no_meaning_class)
            tmp_res = choose_max_plus(self.const_class,
                                 self.multi_value_class,
                                 self.counter_class,
                                 self.sensor_class,
                                 self.no_meaning_class)
            loc = tmp_res.classfy_begin_loc + tmp_res.classfy_length
            self.final_res.append(tmp_res)
            # print("i am happy:::  " + str(tmp_res.classfy_class))

            # 一轮迭代完成，需要进行归空操作
            self.const_class = None
            self.multi_value_class = None
            self.sensor_counter_class = None

            self.counter_class = None
            self.sensor_class = None
            self.no_meaning_class = None

            begin_loc = tmp_res.classfy_begin_loc
            l = tmp_res.classfy_length
            end_loc = begin_loc + l - 1


            # 可行区间更新
            target_loc = []
            target_section = None
            target_b = None
            target_e = None

            for section in self.available_set_section:
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

            if target_b is not None and target_e is not None:
                self.available_set_section.remove((target_b, target_e))
            for item in target_loc:
                self.available_set_section.add(item)
            #print("已经完成分类过程")

    def save_results(self):
        self.result_dict['can_id'].append(self.can_id)
        for classfy_result in self.final_res:
            self.result_dict['start_bit'].append(classfy_result.classfy_begin_loc)
            self.result_dict['end_bit'].append(classfy_result.classfy_begin_loc + classfy_result.classfy_length - 1)
            self.result_dict['type'].append(classfy_result.classfy_class)
            self.result_dict['value_range'].append(classfy_result.classfy_value_store)
            self.result_dict['can_id'].append('')
            print(str(classfy_result.classfy_begin_loc) + " " + \
                  str(classfy_result.classfy_begin_loc + classfy_result.classfy_length - 1) \
                  + " " + str(classfy_result.classfy_class) + " " + str(classfy_result.classfy_score) + " ")
        self.result_dict['can_id'].pop()

    def show_results(self):
        print(len(self.final_res))
        for classfy_result in self.final_res:
            print(str(classfy_result.classfy_begin_loc) + " " + \
                  str(classfy_result.classfy_begin_loc + classfy_result.classfy_length - 1) \
                  + " " + str(classfy_result.classfy_class) + " " + str(classfy_result.classfy_score) + " ")
            for number in classfy_result.classfy_value_store:
                # 将二进制数字打印出来，方便程序调试
                print(bin(number))
                # 大致上稍微改了一下逻辑
            print("          ")
    # 这个新的函数，检查是传感器还是计数器，需要有某个特定的判断条件
    # 按位划分时，就需要将sensor和counter直接区分出来，sensor最好用比较复杂的方法进行区分
    # 以下的check函数可以暂时忽略掉
    def check_sensor_or_counter(self):
        # 用于控制输出的内容
        times = 0

        for classfy_result in self.final_res:
            # 表明在这里是计数器类型的
            if classfy_result.classfy_class == 2:
                # 在这里需要前向差分序列

                data_in_value = []

                begin_loc = classfy_result.classfy_begin_loc
                end_loc = classfy_result.classfy_length + begin_loc - 1

                for data in self.data_list:
                    data_in_value.append(int(data.data_in_binary[begin_loc:end_loc + 1]))
                length = end_loc - begin_loc + 1

                plt.plot(data_in_value[0:5000], "o")
                plt.show()
                data_in_value = pd.Series(data_in_value)
                data_in_value = data_in_value.diff()
                data_in_value = np.unique(data_in_value)
                print(data_in_value[50:100])

                # 计数器应当只有两个差分，但是别的会有多个差分

    def show_counter(self):
        # 用于控制输出的内容
        times = 0

        for classfy_result in self.final_res:
            # 表明在这里是计数器类型的
            if classfy_result.classfy_class == self.counter_tag:
                # 在这里需要前向差分序列

                data_in_value = []
                data_in_value_binary = []

                begin_loc = classfy_result.classfy_begin_loc
                end_loc = classfy_result.classfy_length + begin_loc - 1

                for data in self.data_list:
                    data_in_value.append(int(data.data_in_binary[begin_loc:end_loc + 1]))
                    data_in_value_binary.append(data.data_in_binary[begin_loc:end_loc + 1])
                length = end_loc - begin_loc + 1

                # plt.plot(np.log2(data_in_value[0:500]), "o")
                plt.plot(data_in_value_binary[850:900], "o")
                plt.show()

                # 以下是不太合理的查分过程
                data_in_value = pd.Series(data_in_value)
                data_in_value = data_in_value.diff()
                data_in_value = np.unique(data_in_value)
                print(data_in_value[50:100])

                # 计数器应当只有两个差分，但是别的会有多个差分
    def show_sensor(self):
        # 用于控制输出的内容
        times = 0

        for classfy_result in self.final_res:
            # 表明在这里是计数器类型的
            if classfy_result.classfy_class == self.sensor_tag:
                # 在这里需要前向差分序列

                data_in_value = []
                data_in_value_binary = []

                begin_loc = classfy_result.classfy_begin_loc
                end_loc = classfy_result.classfy_length + begin_loc - 1

                for data in self.data_list:
                    data_in_value.append(int(data.data_in_binary[begin_loc:end_loc + 1]))
                    data_in_value_binary.append(data.data_in_binary[begin_loc:end_loc + 1])
                length = end_loc - begin_loc + 1

                # plt.plot(np.log2(data_in_value[0:500]), "o")
                plt.plot(data_in_value_binary[0:5000], "o")
                plt.show()

                # 以下是不太合理的查分过程
                data_in_value = pd.Series(data_in_value)
                data_in_value = data_in_value.diff()
                data_in_value = np.unique(data_in_value)
                print(data_in_value[50:100])
