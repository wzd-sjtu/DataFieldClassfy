# 本文件用于读取数据
from used_class import hex_str_to_binary_str, \
    choose_max, Single_Data, \
    Classfy_Results
import pandas as pd
import numpy as np

path = ".././source/origin_source/data.csv"
write_path = ".././source/origin_source/result.csv"
nrows = 1000000



class Data():
    def __init__(self):
        self.all_data = pd.read_csv(path,  nrows=nrows)
        self.CANID_set = set(self.all_data['can_id'])
        self.result_dict = {}
        self.result_dict['can_id']=[]
        self.result_dict['start_bit']=[]
        self.result_dict['end_bit']=[]
        self.result_dict['type']=[]


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
        
        self.result_dataframe = pd.DataFrame(data = self.result_dict,columns=['can_id','start_bit','end_bit','type'])
        self.result_dataframe.to_csv(write_path,index=False,sep=',')
    
    def reset(self):
        self.data_list = []
        self.data_length = 0
        # classfy_results_list是分好类的数据
        self.classfy_results_list = []

        # 用于存储每一轮迭代中每种类别的最优解
        self.const_class = None
        self.multi_value_class = None
        self.sensor_counter_class = None
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
    # 应当先导入数据集，再设置数据字段长度
    def set_data_length(self):
        self.data_length = len(self.data_list[0].data_in_binary)
        return
    def initial_classfy_data(self):
        for i in range(0, self.data_length):
            for j in range(0, self.data_length - i):
                tmp_classfy_data = Classfy_Results()
                tmp_classfy_data.classfy_begin_loc = i
                tmp_classfy_data.classfy_length = j + 1
                self.classfy_results_list.append(tmp_classfy_data)
        return
    # 处理分类数据，这里面有分类的详细标准
    def process_classfy_data(self):
        for classfy_result in self.classfy_results_list:
            s = set([])
            begin_loc = classfy_result.classfy_begin_loc
            end_loc = classfy_result.classfy_length + begin_loc - 1

            for data in self.data_list:
                s.add(data.data_in_binary[begin_loc:end_loc + 1])
            length = end_loc - begin_loc + 1

            # 以下的注释代表了许多种情况的
            if len(s) == 1:
                # classfy_result.classfy_class = "const"
                classfy_result.classfy_class = 0
                classfy_result.classfy_score = length
            # elif len(s) <= min(2**(0.5*length), 12):
            elif len(s) <= min(2**(0.5*length), 12) and length >= 3:
                # classfy_result.classfy_class = "multi-value"
                classfy_result.classfy_class = 1
                classfy_result.classfy_score = length
            elif length >= 3:
                # classfy_result.classfy_class = "sensor or counter"
                # 以下是score的计算方法
                classfy_result.classfy_class = 2
                classfy_result.classfy_score = (len(s) * len(s) / 2 ** length)
                # classfy_result.classfy_score = (len(s) / 2 ** length)
            else:
                # 第四类，可以直接忽略
                classfy_result.classfy_class = 3
                classfy_result.classfy_score = length
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
                        if classfy_result.classfy_class == 0:
                            if self.const_class is None:
                                self.const_class = classfy_result
                            else:
                                if self.const_class.classfy_score < classfy_result.classfy_score:
                                    self.const_class = classfy_result
                        elif classfy_result.classfy_class == 1:
                            if self.multi_value_class is None:
                                self.multi_value_class = classfy_result
                            else:
                                if self.multi_value_class.classfy_score < classfy_result.classfy_score:
                                    self.multi_value_class = classfy_result
                        elif classfy_result.classfy_class == 2:
                            if self.sensor_counter_class is None:
                                self.sensor_counter_class = classfy_result
                            else:
                                if self.sensor_counter_class.classfy_score < classfy_result.classfy_score:
                                    self.sensor_counter_class = classfy_result
                        elif classfy_result.classfy_class == 3:
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
            tmp_res = choose_max(self.const_class, self.multi_value_class, self.sensor_counter_class, self.no_meaning_class)
            loc = tmp_res.classfy_begin_loc + tmp_res.classfy_length
            self.final_res.append(tmp_res)
            # print("i am happy:::  " + str(tmp_res.classfy_class))

            # 一轮迭代完成，需要进行归空操作
            self.const_class = None
            self.multi_value_class = None
            self.sensor_counter_class = None
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
            self.result_dict['can_id'].append('')
            print(str(classfy_result.classfy_begin_loc) + " " + \
                  str(classfy_result.classfy_begin_loc + classfy_result.classfy_length - 1) \
                  + " " + str(classfy_result.classfy_class) + " " + str(classfy_result.classfy_score) + " ")
        self.result_dict['can_id'].pop()