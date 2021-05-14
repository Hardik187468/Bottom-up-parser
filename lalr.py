import sys

from impl import *
import state

lis = ["I->E", "E->E+T|T", "T->(E)|i"]
inp = ""


class parser():
    def __init__(self, parent=None):

        self.init()
        self.read_input()
        files = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\item.txt", 'w')
        self.disp()
        self.disp_first()
        self.disp_lr1_states(files)
        self.disp_lalr_states(files)
        files.close()
        self.disp_parse_table()
        self.check_changed()
        if inp != "":
            self.disp_parsing()

    def init(self):
        self.grammar = []
        self.augment_grammar = []

        self.first = {}

        self.term = []
        self.non_term = []

        self.states = []
        self.lalr_states = []
        self.parse_table = []
        State.state_count = -1
        lalrState.state_count = 0

    def check_changed(self):
        self.changed = True

    def read_input(self):
        self.init()
        global lis  # converting into list of lines
        lines_list = lis
        try:
            for line in lines_list:
                line = line.replace(' ', '')

                if line != '':
                    line_list = line.split('->')

                    if line_list[0].isupper() and line_list[1] != '':
                        if '|' in line_list[1]:
                            prod_list = line_list[1].split('|')
                            for prod in prod_list:
                                self.grammar.append([line_list[0], prod])
                        else:
                            self.grammar.append(line_list)
                    else:

                        print("Invalid grammar")
                        self.grammar = []

            if self.grammar != []:
                term_and_nonterm(self.grammar, self.term, self.non_term)
                calculate_first(self.grammar, self.first, self.term, self.non_term)
                get_augmented(self.grammar, self.augment_grammar)
                find_states(self.states, self.augment_grammar, self.first, self.term, self.non_term)
                combine_states(self.lalr_states, self.states)
                get_parse_table(self.parse_table, self.lalr_states, self.augment_grammar)
                self.changed = False

        except (KeyError, IndexError):
            print("Invalid grammar")
            self.init()

    ############################         DISPLAY          ################################

    def disp(self):
        l = []
        if self.grammar != []:
            for prod in self.grammar:
                s = prod[0] + ' -> ' + prod[1] + '\n'
                print(s)
                print("\nNon Terminals : " + ' '.join(self.non_term) + "\nTerminals : " + ' '.join(self.term))

    def disp_first(self):

        if self.first != {}:

            for key, value in self.first.items():
                if key in self.non_term:
                    print('First(' + key + ') : ' + ' '.join(value) + '\n')

    def disp_lr1_states(self, files):

        if self.states != []:

            print("Number of LR(1) states : " + str(self.states[len(self.states) - 1].state_num + 1), file=files)
            for state in self.states:
                print('----------------------------------------------------------------', file=files)
                if state.state_num == 0:
                    print("\nI" + str(state.state_num) + ' : ' + '\n', file=files)
                else:
                    print("\nI" + str(state.state_num) + ' : ' + ' goto ( I' + str(state.parent[0]) + " -> '" + str(
                        state.parent[1]) + "' )\n", file=files)
                for item in state.state:
                    print(item[0] + ' -> ' + item[1] + ' ,  [ ' + ' '.join(item[2]) + ' ]', file=files)
                if state.actions != {}:
                    print('\nActions : ', file=files)
                    for k, v in state.actions.items():
                        print(str(k) + ' -> ' + str(abs(v)) + '\t', file=files)

    def disp_lalr_states(self, files):

        if self.lalr_states != []:

            print("Number of LALR states : " + str(lalrState.state_count), file=files)
            for state in self.lalr_states:
                print('----------------------------------------------------------------', file=files)
                if state.state_num == 0:
                    print("\nI" + str(state.state_num) + ' : ' + '\tGot by -> ' + str(state.parent_list) + '\n',
                          file=files)
                else:
                    print("\nI" + str(state.state_num) + ' : ' + ' goto ( I' + str(state.parent[0]) + " -> '" + str(
                        state.parent[1]) + "' )" + '\tGot by -> ' + str(state.parent_list) + '\n', file=files)
                for item in state.state:
                    print(item[0] + ' -> ' + item[1] + ' ,   [ ' + ' '.join(item[2]) + ' ]', file=files)
                if state.actions != {}:
                    print('\nActions : ', file=files)
                    for k, v in state.actions.items():
                        print(str(k) + ' -> ' + str(abs(v)) + '\t', file=files)

    def disp_parse_table(self):

        files = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\table.txt", 'w')
        if self.grammar != []:

            all_symb = []
            all_symb.extend(self.term)
            all_symb.append('$')
            all_symb.extend(self.non_term)
            if 'e' in all_symb:
                all_symb.remove('e')

            head = '{0:12}'.format(' ')
            for X in all_symb:
                head = head + '{0:12}'.format(X)
            print(head + '\n', file=files)
            s = '------------' * len(all_symb)
            print(s, file=files)

            for index, state in enumerate(self.parse_table):
                line = '{0:<12}'.format(index)
                for X in all_symb:
                    if X in state.keys():
                        if X in self.non_term:
                            action = state[X]
                        else:
                            if state[X] > 0:
                                action = 's' + str(state[X])
                            elif state[X] < 0:
                                action = 'r' + str(abs(state[X]))
                            elif state[X] == 0:
                                action = 'accept'

                        line = line + '{0:<12}'.format(action)
                    else:
                        line = line + '{0:<12}'.format("")

                print(line, file=files)
                print(s, file=files)
        files.close()

    def disp_parsing(self):

        if self.grammar != []:
            global inp
            self.parse(self.parse_table, self.augment_grammar, inp)

    def parse(self, parse_table, augment_grammar, inpt):
        files = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\stack.txt", 'w')
        inpt = list(inpt + '$')
        stack = [0]
        a = inpt[0]
        try:
            head = '{0:40} {1:40} {2:40}'.format("Stack", "Input", "Actions")
            print(head, file=files)
            while True:
                string = str('\n{0:<40} {1:<40} '.format('{}'.format(stack), ''.join(inpt)))

                s = stack[len(stack) - 1]
                action = parse_table[s][a]
                if action > 0:
                    inpt.pop(0)
                    stack.append(action)
                    print(string + 'Shift ' + a + '\n', file=files)
                    a = inpt[0]
                elif action < 0:
                    prod = augment_grammar[-action]
                    if prod[1] != 'e':
                        for i in range(len(prod[1])):
                            stack.pop()
                    t = stack[len(stack) - 1]
                    stack.append(parse_table[t][prod[0]])
                    print(string + 'Reduce ' + prod[0] + ' -> ' + prod[1] + '\n', file=files)
                elif action == 0:
                    print('ACCEPT\n', file=files)
                    break
        except KeyError:
            print('\n\nERROR\n', file=files)
        files.close()


def main(l, inpu):
    global lis, inp
    lis = l
    inp = inpu
    myapp = parser()


