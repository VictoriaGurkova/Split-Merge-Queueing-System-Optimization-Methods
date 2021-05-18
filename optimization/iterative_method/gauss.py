def fancy_print(a, b, selected):
    for row in range(len(b)):
        print("(", end='')
        for col in range(len(a[row])):
            print("\t{1:10.2f}{0}".format(" " if (selected is None
                                                  or selected != (row, col)) else "*", a[row][col]), end='')
        print("\t) * (\tX{0}) = (\t{1:10.2f})".format(row + 1, b[row]))


def swap_rows(a, b, row1, row2):
    a[row1], a[row2] = a[row2], a[row1]
    b[row1], b[row2] = b[row2], b[row1]


def divide_row(a, b, row, divider):
    a[row] = [i / divider for i in a[row]]
    b[row] /= divider


def combine_rows(a, b, row, source_row, weight):
    a[row] = [(i + j * weight) for i, j in zip(a[row], a[source_row])]
    b[row] += b[source_row] * weight


def gauss(a, b):
    column = 0
    while column < len(b):
        print("Ищем максимальный по модулю элемент в {0}-м столбце:".format(column + 1))
        current_row = None
        for r in range(column, len(a)):
            if current_row is None or abs(a[r][column]) > abs(a[current_row][column]):
                current_row = r
        if current_row is None:
            print("решений нет")
            return None
        fancy_print(a, b, (current_row, column))
        if current_row != column:
            print("Переставляем строку с найденным элементом повыше:")
            swap_rows(a, b, current_row, column)
            fancy_print(a, b, (column, column))
        print("Нормализуем строку с найденным элементом:")
        divide_row(a, b, column, a[column][column])
        fancy_print(a, b, (column, column))
        print("Обрабатываем нижележащие строки:")
        for r in range(column + 1, len(a)):
            combine_rows(a, b, r, column, -a[r][column])
        fancy_print(a, b, (column, column))
        column += 1
    print("Матрица приведена к треугольному виду, считаем решение")
    x = [0 for _ in b]
    for i in range(len(b) - 1, -1, -1):
        x[i] = b[i] - sum(x * j for x, j in zip(x[(i + 1):], a[i][(i + 1):]))
    print("Получили ответ:")
    print("\n".join("x{0} =\t{1:10.2f}".format(i + 1, x) for i, x in
                    enumerate(x)))
    return x

