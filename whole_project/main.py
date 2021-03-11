from data_process import Data


if __name__ == '__main__':
    target_data = Data()
    path = ".././source/origin_source/C1_data.xlsx"
    # 首先还原出我原先版本的结构
    # 最少要读入5行数据，否则会报错
    # 首先处理500的数据量级
    nrows = 5000

    # 数据读入并设置基本参数
    target_data.reset()
    target_data.store_data_with_can_matrix_for_single_canid(path, nrows)
    target_data.set_data_length()

    # 进行分类
    target_data.initial_classfy_data()
    target_data.process_classfy_data()

    # 贪心算法求最优解
    target_data.greedy_find_solution()

    # 显示
    target_data.show_results()
    target_data.check_sensor_or_counter()