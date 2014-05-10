from functools import reduce
import math

__author__ = 'Olexandr'


# scalar multiplication
def dot(v1, v2, features):
    res = 0
    for i in range(features):
        res += v1[i] * v2[i]
    return res


def read_csv_file(name, w_sep="\t", l_sep="\n"):
    file = open(name, 'r')
    lines = file.readlines()
    file.close()
    return list(map(lambda line: list(map(lambda item: int(item), str(line).replace(l_sep, "").split(w_sep))), lines))


def list_to_tuple(list_data):
    data = {}
    max_val = 0
    total = len(list_data)
    for i in list_data:
        data[i[0]] = {}
    for i in list_data:
        data[i[0]][i[1]] = i[2]
        max_val = max(max_val, i[1])

    return data, max_val+1, total


def print_array(prefix, array):
    print(prefix + "\t" + reduce(lambda x, y: str(x) + "\t" + str(y), array))


def print_all(mu, b_u, b_v, u_f, v_f):
    print("\nmu:\t" + str(mu))
    print_array("User base:", b_u)
    print_array("Item base:", b_v)
    print("\nUser features")
    for i in u_f.keys():
        print_array("user " + str(i) + ":", u_f[i].values())
    print("\nItem features:")
    for i in v_f.keys():
        print_array("item " + str(i) + ":", v_f[i].values())


def main(features):
    lambda2 = 0.0
    eta = 0.1
    data, urls, total = list_to_tuple(read_csv_file("habr.csv"))
    users = len(data)
    print("Read " + str(users) + " users and " + str(urls) + " urls.")

    # инициализируем
    mu = 0
    b_u = [0]*users
    b_v = [0]*urls
    u_f = {}
    for i in range(users):
        u_f[i] = {}
        for j in range(features):
            u_f[i][j] = 0.1
    v_f = {}
    for i in range(urls):
        v_f[i] = {}
        for j in range(features):
            v_f[i][j] = 0.05 * j
    iteration_number = 0
    root_mean_square_error = 1
    old_root_mean_square_error = 0
    threshold = 0.01
    #todo: all ok
    # обучение SVD: обучаем, пока не сойдётся
    while math.fabs(old_root_mean_square_error - root_mean_square_error) > 0.00001:
        old_root_mean_square_error = root_mean_square_error
        root_mean_square_error = 0
        for i in data.keys():
            for j in data[i].keys():
                # ошибка
                error = data[i][j] - (mu + b_u[i] + b_v[j] + dot(u_f[i], v_f[j], features))
                # квадрат ошибки
                root_mean_square_error += error * error
                # применяем правила апдейта для базовых предикторов
                mu += eta * error
                b_u[i] += eta * (error - lambda2 * b_u[i])
                b_v[j] += eta * (error - lambda2 * b_v[j])
                # и для векторов признаков
                for f in range(features):
                    u_f[i][f] += eta * (error * v_f[j][f] - lambda2 * u_f[i][f])
                    v_f[j][f] += eta * (error * u_f[i][f] - lambda2 * v_f[j][f])
        iteration_number += 1
        # нормируем суммарную ошибку, чтобы получить RMSE
        root_mean_square_error = math.sqrt(root_mean_square_error / total)
        print("Iteration " + str(iteration_number) + ":\tRMSE = " + str(root_mean_square_error))
        # если root mean squared error меняется мало, нужно уменьшить скорость обучения
        if root_mean_square_error > old_root_mean_square_error - threshold:
            eta *= 0.66
            threshold *= 0.5

    print_all(mu, b_u, b_v, u_f, v_f)
    user = 0
    item = 2
    print(mu + b_u[user] + b_v[item] + reduce(lambda x, y: x*y, u_f[user], 1) + reduce(lambda x, y: x*y, v_f[item], 1))


main(2)