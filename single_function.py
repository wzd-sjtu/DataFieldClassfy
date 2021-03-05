class Single_Data:
    can_id = None
    time = None
    data_in_hex = None
    data_in_binary = None

class Classfy_Results:
    classfy_begin_loc = None
    classfy_length = None
    classfy_class = None # 可以是0/1/2 分别代表const、multi-value、snesor/counter 三中类型
    classfy_score = None # 合适的打分

hex2bin_map = {
   "0":"0000",
   "1":"0001",
   "2":"0010",
   "3":"0011",
   "4":"0100",
   "5":"0101",
   "6":"0110",
   "7":"0111",
   "8":"1000",
   "9":"1001",
   "A":"1010",
   "B":"1011",
   "C":"1100",
   "D":"1101",
   "E":"1110",
   "F":"1111",
}
# 0001_0010_0011_0100
def hex_str_to_binary_str(hex_str):
    tmp = ""
    for i in hex_str:
        tmp = tmp + hex2bin_map[i]
    return tmp

# print(hex_str_to_binary_str("ABCD"))

# 这段代码是核心逻辑的问题出处，决定了后文贪心算法最后的结果

'''
def choose_max(s1, s2, s3):
    # 这里的logic应当是什么呢？暂时是未知的
    if s1 is None and s2 is None and s3 is None:
        return None
    if s1 is None:
        s1 = Classfy_Results()
        s1.classfy_score = 0
    if s2 is None:
        s2 = Classfy_Results()
        s2.classfy_score = 0
    if s3 is None:
        s3 = Classfy_Results()
        s3.classfy_score = 0

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
# 转换为另一种选择方式，type作为更加优先的选择，从而提高算法的效率


def choose_max(s1, s2, s3):
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
