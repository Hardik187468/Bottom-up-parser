from state import *


# def read_input(grammar):
##    file_name = "grammar.txt"
#    file_name = input("Enter file name : ")
#    try:
#        file = open(file_name,'r')
#    except IOError:
#        print("file not found!")
#        sys.exit()
#
#    lines_list = file.readlines()
#
#    for line in lines_list:
#        line = line.strip('\n')
#        line = line.replace(' ' ,'')
#
#        if line != '':
#            line_list = line.split('->')
#
#            if line_list[0].isupper():
#                if '|' in line_list[1]:
#                    prod_list = line_list[1].split('|')
#                    for prod in prod_list:
#                        grammar.append([line_list[0],prod])
#                else:
#                    grammar.append(line_list)
#            else:
#                print("Invalid grammar")
#                sys.exit(0)
#
#    for prod in grammar:
#        print(prod[0],'->',prod[1])


def term_and_nonterm(grammar, term, non_term):
    for prod in grammar:
        if prod[0] not in non_term:
            non_term.append(prod[0])
        for char in prod[1]:
            if not char.isupper():
                if char not in term:
                    term.append(char)


def calculate_first(grammar, first, term, non_term):
    for t in term:
        first[t] = t
    for nt in non_term:
        first[nt] = set({})
    for nt in non_term:
        get_first(nt, grammar, first, term)


def get_first(nt, grammar, first, term):
    for prod in grammar:
        if nt in prod[0]:
            rhs = prod[1]
            first_char = rhs[0]
            if first_char in term:
                first[nt].add(first[first_char])
            else:
                if not first[first_char] and nt != first_char:
                    get_first(first_char, grammar, first, term)

                i = 0
                while i < len(rhs) and 'e' in first[rhs[i]]:
                    for elem in first[rhs[i]]:
                        if 'e' != elem:
                            first[nt].add(elem)
                    i += 1
                if i == len(rhs):
                    first[nt].add('e')
                else:
                    for elem in first[rhs[i]]:
                        first[nt].add(elem)


def get_augmented(grammar, augment_grammar):
    augment_grammar.append([grammar[0][0] + "'", grammar[0][0]])
    augment_grammar.extend(grammar)


def closure(I, augment_grammar, first, non_term):
    while True:
        new_item_added = False
        for item in I:
            cursor_pos = item[1].index('.')
            if cursor_pos == (len(item[1]) - 1):
                continue
            next_char = item[1][cursor_pos + 1]
            if next_char in non_term:
                for prod in augment_grammar:
                    if next_char == prod[0]:
                        if prod[1] == 'e':
                            rhs = 'e.'
                        else:
                            rhs = '.' + prod[1]
                        la = []  # look ahead
                        if cursor_pos < (len(item[1]) - 2):
                            Ba = item[1][cursor_pos + 2]
                            for firs in first[Ba]:
                                if 'e' == firs:
                                    for elem in item[2]:
                                        if elem not in la:
                                            la.append(elem)
                                else:
                                    if firs not in la:
                                        la.append(firs)
                        else:
                            la = deepcopy(item[2])

                        new_item = [next_char, rhs, la]  # structure of each item

                        if new_item not in I:
                            same_item_with_diff_la = False
                            for item_ in I:
                                if item_[0] == new_item[0] and item_[1] == new_item[1]:
                                    same_item_with_diff_la = True
                                    for las in la:
                                        if las not in item_[2]:
                                            item_[2].append(las)
                                            new_item_added = True
                            if not same_item_with_diff_la:
                                I.append(new_item)
                                new_item_added = True

        if not new_item_added:
            break


def goto(I, X, augment_grammar, first, non_term):
    J = []
    for item in I:
        cursor_pos = item[1].index('.')
        if cursor_pos < len(item[1]) - 1:
            next_char = item[1][cursor_pos + 1]
            if next_char == X:
                new_rhs = item[1].replace('.' + X, X + '.')
                new_item = [item[0], new_rhs, item[2]]
                J.append(new_item)
    closure(J, augment_grammar, first, non_term)
    return J


def isSame(states, new_state, I, X):
    for J in states:
        if J.state == new_state:
            I.update_goto(X, J)
            return True
    return False


def init_first(augment_grammar, first, non_term):
    I = [[augment_grammar[0][0], '.' + augment_grammar[0][1], ['$']]]
    closure(I, augment_grammar, first, non_term)
    return I


def find_states(states, augment_grammar, first, term, non_term):
    first_state = init_first(augment_grammar, first, non_term)
    I = State(first_state)
    states.append(I)
    all_symb = non_term + term
    while True:
        new_state_added = False
        for I in states:
            for X in all_symb:
                new_state = goto(I.state, X, augment_grammar, first, non_term)  # goto(I,X)
                if (new_state != []) and not isSame(states, new_state, I, X):
                    N = State(new_state)
                    I.update_goto(X, N)
                    N.update_parentName(I, X)
                    states.append(N)
                    new_state_added = True

        if not new_state_added:
            break


def combine_states(lalr_states, states):
    first = lalrState(states[0])
    first.update_parentList(states[0])
    lalr_states.append(first)
    mapping = [0]
    for I in states[1:]:
        state_found = False
        for J in lalr_states:
            if J.state[0][:2] == I.state[0][:2]:
                state_found = True
                mapping.append(J.state_num)
                J.update_parentList(I)
                for index, item in enumerate(J.state):
                    for la in I.state[index][2]:
                        if la not in item[2]:
                            item[2].append(la)

        if not state_found:
            new_state = lalrState(I)
            new_state.update_parentList(I)

            lalr_states.append(new_state)
            mapping.append(new_state.state_num)

    for I in lalr_states:
        I.update_mapping(mapping)


def get_parse_table(parse_table, states, augmented_grammar):  # here states -> lalr_states
    ambiguous = False
    for index, I in enumerate(states):
        parse_table.append(I.actions)
        for item in I.state:
            rhs_list = item[1].split('.')
            if rhs_list[1] == '':
                prod_no = augmented_grammar.index([item[0], rhs_list[0]])
                for la in item[2]:
                    if la in parse_table[index].keys():
                        #                        print('Ambiguous grammar!!')
                        ambiguous = True
                    else:
                        parse_table[index][la] = -prod_no

    if ambiguous:
        print("Ambiguous Grammar!!\n\nGiving priority to Shift over Reduce")

# def parse(parse_table,augment_grammar,inpt):
#    inpt = list(inpt+'$')
#    stack = [0]
#    a = inpt[0]
#    try:
#        while True:
#            print('\nstack : {0:20}'.format(stack),'input:',str(inpt),end=' ')
#            s = stack[len(stack)-1]
#            action = parse_table[s][a]
#            if action > 0:
#                inpt.pop(0)
#                stack.append(action)
#                print('Shifting :',a)
#                a = inpt[0]
#            elif action < 0:
#                prod = augment_grammar[-action]
#                if prod[1] != 'e':
#                    for i in range(len(prod[1])):
#                        stack.pop()
#                t = stack[len(stack)-1]
#                stack.append(parse_table[t][prod[0]])
#                print('Reducing :',prod)
#            elif action == 0:
#                print('ACCEPT')
#                break
#    except KeyError:
#        print('ERROR')
#


# def display(grammar,augment_grammar,term,non_term,first, states,lalr_states):
#    print('grammar')
#    for prod in grammar:
#        print(prod)
#
#    print('term :',term,'\nnon term :',non_term)
#
#    print('first:')
#    for nt in non_term:
#        print(nt,'->',first[nt])
#
#    print('augment grammar :')
#    for prod in augment_grammar:
#        print(prod)
#
#
#    print('\n\nLR(1) items : ',end='')
#    for state in states:
#        print("\n\nI",state.state_num,':', ' goto',state.parent, sep = '')
#        for item in state.state:
#            print(item)
#        if state.actions != {}:
#            print('\nActions : ',end='')
#            for k,v in state.actions.items():
#                print(k,'->',v,sep='',end='  ')
#
#
#
#    print('\n\nLALR items : ',end ='')
#    for state in lalr_states:
#        print("\n\nI",state.state_num,':', ' goto', state.parent,'\tGot by -> ',state.parent_list, sep = '')
#        for item in state.state:
#            print(item)
#        if state.actions != {}:
#            print('Actions : ',end='')
#            for k,v in state.actions.items():
#                print(k,'->',v,sep='',end='  ')
#

