from data_process import Data

if __name__ == '__main__':
    target_data = Data()
    path = ".././source/origin_source/C9_data.xlsx"
    # 最少要读入5行数据，否则会报错
    nrows = 1000

    # 数据读入并设置基本参数
    target_data.read_and_store_data_with_can_matrix(path, nrows)
    target_data.set_data_length()

    # 进行分类
    target_data.initial_classfy_data()
    target_data.process_classfy_data()

    # 贪心算法求最优解
    target_data.greedy_find_solution()

    # 显示
    target_data.show_results()