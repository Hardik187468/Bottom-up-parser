import sys
import shlex
import csv
import termtables as tt
import numpy as np

terminal = []




def main(input_string):
    grammar = open('grammarly.txt', 'r')
    master = {}
    master_list = []
    new_list = []
    non_terminals = []
    for row2 in grammar:

        if '->' in row2:
            # new production
            if len(new_list) == 0:
                start_state = row2[0]
                non_terminals.append(row2[0])
                new_list = []
                new_list.append(row2.rstrip('\n'))
            else:
                master_list.append(new_list)
                del new_list
                new_list = []
                new_list.append(row2.rstrip('\n'))
                non_terminals.append(row2[0])


        elif '|' in row2:
            new_list.append(row2.rstrip('\n'))

    master_list.append(new_list)

    for x in range(len(master_list)):
        for y in range(len(master_list[x])):
            master_list[x][y] = [s.replace('|', '') for s in master_list[x][y]]
            master_list[x][y] = ''.join(master_list[x][y])
            master[master_list[x][y]] = non_terminals[x]

    for key, value in master.items():
        if '->' in key:
            length = len(key)
            for i in range(length):
                if key[i] == '-' and key[i + 1] == ">":
                    index = i + 2
                    break
            var_key = key
            new_key = key[index:]

    var = master[var_key]
    del master[var_key]
    master[new_key] = var

    order_table = []
    with open('order.csv', 'r') as file2:
        order = csv.reader(file2)
        for row in order:
            order_table.append(row)

    operators = order_table[0]

    input_ind = list(shlex.shlex(input_string))
    input_ind.append('$')

    ###### Analysis
    stack = []

    stack.append('$')

    data = []
    header = ["Stack", "Input", "Precedence relation", "Action"]

    vlaag = 1
    while vlaag:
        if input_ind[0] == '$' and len(stack) == 2:
            vlaag = 0

        length = len(input_ind)

        buffer_inp = input_ind[0]
        temp1 = operators.index(str(buffer_inp))
        if stack[-1] in non_terminals:
            buffer_stack = stack[-2]
        else:
            buffer_stack = stack[-1]
        temp2 = operators.index(str(buffer_stack))
        # print buffer_inp, buffer_stack

        precedence = order_table[temp2][temp1]

        if precedence == '<':
            action = 'shift'
        elif precedence == '>':
            action = 'reduce'
        lst = []
        lst.append(str(stack))
        lst.append(str(input_ind))
        lst.append(str(precedence))
        lst.append(str(action))
        data.append(lst)
        if action == 'shift':
            stack.append(buffer_inp)
            input_ind.remove(buffer_inp)
        elif action == 'reduce':
            for key, value in master.items():
                var1 = ''.join(stack[-1:])
                var2 = ''.join(stack[-3:])
                if str(key) == str(buffer_stack):
                    stack[-1] = value
                    break
                elif key == var1 or stack[-3:] == list(var1):
                    stack[-3:] = value
                    break
                elif key == var2:
                    stack[-3:] = value
        del buffer_inp, temp1, buffer_stack, temp2, precedence
        if vlaag == 0:
            files = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\stack.txt", 'w')
            print("Accepted!!", file=files)
            data[-1][-1] = "accept"
            print(header)
            print(data)
            parsing_table = tt.to_string(data=data, header=header, style=tt.styles.ascii_thin_double, padding=(0, 1))
            print(parsing_table, file=files)
            files.close()
    return 2


def stringcheck():
    files = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\table.txt", 'w')
    a = terminal
    a.append('$')
    print(a, file=files)
    l = list("abcdefghijklmnopqrstuvwxyz")
    o = list('(/*%+-)')
    p = list('(/*%+-)')
    n = np.empty([len(a) + 1, len(a) + 1], dtype=str, order="C")
    for j in range(1, len(a) + 1):
        n[0][j] = a[j - 1]
        n[j][0] = a[j - 1]
    for i in range(1, len(a) + 1):
        for j in range(1, len(a) + 1):
            if ((n[i][0] in l) and (n[0][j] in l)):
                n[i][j] = " "
            elif ((n[i][0] in l)):
                n[i][j] = ">"
            elif ((n[i][0] in o) and (n[0][j] in o)):
                if (o.index(n[i][0]) <= o.index(n[0][j])):
                    n[i][j] = ">"
                else:
                    n[i][j] = "<"
            elif ((n[i][0] in o) and n[0][j] in l):
                n[i][j] = "<"
            elif (n[i][0] == "$" and n[0][j] != "$"):
                n[i][j] = "<"
            elif (n[0][j] == "$" and n[i][0] != "$"):
                n[i][j] = ">"
            else:
                break
    print("The Operator Precedence Relational Table\n=============================================", file=files)
    n[-1][-1] = " "
    n = list(n)
    header = n[0]
    header[0] = " "
    n.pop(0)
    for i in header:
        print("| ", i, end=" ", file=files)
    print(" |", file=files)
    data = []
    for i in n:
        l = []
        for j in i:
            l.append(str(j))
        data.append(l)
    for i in data:
        for j in i:
            print("| ", j, end=" ", file=files)
        print(" |", file=files)
    files.close()
    return True


def grammarcheck(i):
    b = list(i.split("->"))
    global terminal
    f = list("abcdefghijklmnopqrstuvwxyz")
    if (b[0] == " " or b[0] == "" or b[0] in f or len(b) == 1):
        return False
    else:
        b.pop(0)
        b = list(b[0])
        s = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        o = list("(abcdefghijklmnopqrstuvwxyz^/*+-|)")
        sp = ['!', '@', '#', '$', '?', '~', '`', ',', ';', ':', '"', '=', '_', '&', "'", "", " "]
        for i in range(0, len(b), 2):
            if (b[i] == " "):
                g = False
            elif (b[i] in sp):
                g = False
                break
            elif (b[len(b) - 1] in o and ((b[0] == "(" and b[len(b) - 1] == ")") or (b.count("(") == b.count(")")))):
                terminal.append(b[len(b) - 1])
                g = True
            elif (b[i] in f):
                g = True
            elif (b[len(b) - 1] in o):
                g = False
            elif ((i == len(b) - 1) and (b[i] in s)):
                g = True
            elif ((i == len(b) - 1) and (b[i] not in s) and (b[i] in o) and b[i - 1] in o):
                g = True
            elif ((b[i] in s) and (b[i + 1] in o)):
                g = True
            elif ((b[i] in s) and (b[i + 1] in s)):
                g = False
                break
            else:
                g = False
                break
        if (g == True):
            return True
        else:
            return False


def take(lis):
    global terminal
    for i in lis:
        p = str(i)
        k = 0
        for c in p:
            if (c == '+' or c == '-' or c == '*' or c == '/'):
                if (k > 3):
                    terminal.append(c)
            k = k + 1
        if (grammarcheck(i)):
            t = True
        else:
            t = False
            break
    if (t):
        print("Grammar is accepted")
        if (stringcheck()):
            print("String is accepted")
    else:
        print("String is not accepted")
