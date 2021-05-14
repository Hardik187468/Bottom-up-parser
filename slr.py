from grammar1 import Grammar
import argparse


def first_follow(G):
    def union(set_1, set_2):
        set_1_len = len(set_1)
        set_1 |= set_2

        return set_1_len != len(set_1)

    first = {symbol: set() for symbol in G.symbols}
    first.update((terminal, {terminal}) for terminal in G.terminals)
    follow = {symbol: set() for symbol in G.nonterminals}
    follow[G.start].add('$')

    while True:
        updated = False

        for head, bodies in G.grammar.items():
            for body in bodies:
                for symbol in body:
                    if symbol != '^':
                        updated |= union(first[head], first[symbol] - set('^'))

                        if '^' not in first[symbol]:
                            break
                    else:
                        updated |= union(first[head], set('^'))
                else:
                    updated |= union(first[head], set('^'))

                aux = follow[head]
                for symbol in reversed(body):
                    if symbol == '^':
                        continue
                    if symbol in follow:
                        updated |= union(follow[symbol], aux - set('^'))
                    if '^' in first[symbol]:
                        aux = aux | first[symbol]
                    else:
                        aux = first[symbol]

        if not updated:
            return first, follow


class SLRParser:
    def __init__(self, G):
        self.G_prime = Grammar(f"{G.start}' -> {G.start}\n{G.grammar_str}")
        self.max_G_prime_len = len(max(self.G_prime.grammar, key=len))
        self.G_indexed = []

        for head, bodies in self.G_prime.grammar.items():
            for body in bodies:
                self.G_indexed.append([head, body])

        self.first, self.follow = first_follow(self.G_prime)
        self.C = self.items(self.G_prime)
        self.action = list(self.G_prime.terminals) + ['$']
        self.goto = list(self.G_prime.nonterminals - {self.G_prime.start})
        self.parse_table_symbols = self.action + self.goto
        self.parse_table = self.construct_table()

    def CLOSURE(self, I):
        J = I

        while True:
            item_len = len(J)

            for head, bodies in J.copy().items():
                for body in bodies:
                    if '.' in body[:-1]:
                        symbol_after_dot = body[body.index('.') + 1]

                        if symbol_after_dot in self.G_prime.nonterminals:
                            for G_body in self.G_prime.grammar[symbol_after_dot]:
                                J.setdefault(symbol_after_dot, set()).add(
                                    ('.',) if G_body == ('^',) else ('.',) + G_body)

            if item_len == len(J):
                return J

    def GOTO(self, I, X):
        goto = {}

        for head, bodies in I.items():
            for body in bodies:
                if '.' in body[:-1]:
                    dot_pos = body.index('.')

                    if body[dot_pos + 1] == X:
                        replaced_dot_body = body[:dot_pos] + (X, '.') + body[dot_pos + 2:]

                        for C_head, C_bodies in self.CLOSURE({head: {replaced_dot_body}}).items():
                            goto.setdefault(C_head, set()).update(C_bodies)

        return goto

    def items(self, G_prime):
        C = [self.CLOSURE({G_prime.start: {('.', G_prime.start[:-1])}})]

        while True:
            item_len = len(C)

            for I in C.copy():
                for X in G_prime.symbols:
                    if self.GOTO(I, X) and self.GOTO(I, X) not in C:
                        C.append(self.GOTO(I, X))

            if item_len == len(C):
                return C

    def construct_table(self):
        parse_table = {r: {c: '' for c in self.parse_table_symbols} for r in range(len(self.C))}

        for i, I in enumerate(self.C):
            for head, bodies in I.items():
                for body in bodies:
                    if '.' in body[:-1]:  # CASE 2 a
                        symbol_after_dot = body[body.index('.') + 1]

                        if symbol_after_dot in self.G_prime.terminals:
                            s = f's{self.C.index(self.GOTO(I, symbol_after_dot))}'

                            if s not in parse_table[i][symbol_after_dot]:
                                if 'r' in parse_table[i][symbol_after_dot]:
                                    parse_table[i][symbol_after_dot] += '/'

                                parse_table[i][symbol_after_dot] += s

                    elif body[-1] == '.' and head != self.G_prime.start:  # CASE 2 b
                        for j, (G_head, G_body) in enumerate(self.G_indexed):
                            if G_head == head and (G_body == body[:-1] or G_body == ('^',) and body == ('.',)):
                                for f in self.follow[head]:
                                    if parse_table[i][f]:
                                        parse_table[i][f] += '/'

                                    parse_table[i][f] += f'r{j}'

                                break

                    else:  # CASE 2 c
                        parse_table[i]['$'] = 'acc'

            for A in self.G_prime.nonterminals:  # CASE 3
                j = self.GOTO(I, A)

                if j in self.C:
                    parse_table[i][A] = self.C.index(j)

        return parse_table

    def print_info(self):
        files = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\first_follow.txt", 'w')
        def fprint(text, variable):
            print(f'{text:>13}: {", ".join(variable)}',file=files)

        def print_line():
            print(f'+{("-" * width + "+") * (len(list(self.G_prime.symbols) + ["$"]))}',file=files)

        def symbols_width(symbols):
            return (width + 1) * len(symbols) - 1

        print('AUGMENTED GRAMMAR:',file=files)

        for i, (head, body) in enumerate(self.G_indexed):
            print(f'{i:>{len(str(len(self.G_indexed) - 1))}}: {head:>{self.max_G_prime_len}} -> {" ".join(body)}',file=files)

        print(file=files)
        fprint('TERMINALS', self.G_prime.terminals)
        fprint('NONTERMINALS', self.G_prime.nonterminals)
        fprint('SYMBOLS', self.G_prime.symbols)

        print('\nFIRST:',file=files)
        for head in self.G_prime.grammar:
            print(f'{head:>{self.max_G_prime_len}} = {{ {", ".join(self.first[head])} }}',file=files)

        print('\nFOLLOW:',file=files)
        for head in self.G_prime.grammar:
            print(f'{head:>{self.max_G_prime_len}} = {{ {", ".join(self.follow[head])} }}',file=files)

        width = max(len(c) for c in {'ACTION'} | self.G_prime.symbols) + 2
        for r in range(len(self.C)):
            max_len = max(len(str(c)) for c in self.parse_table[r].values())

            if width < max_len + 2:
                width = max_len + 2
        ans = []
        print('\nPARSING TABLE:')
        s = str(f'+{"-" * width}+{"-" * symbols_width(self.action)}+{"-" * symbols_width(self.goto)}+')
        ans.append(s)
        s = str(f'|{"":{width}}|{"ACTION":^{symbols_width(self.action)}}|{"GOTO":^{symbols_width(self.goto)}}|')
        ans.append(s)
        s = str(f'|{"STATE":^{width}}+{("-" * width + "+") * len(self.parse_table_symbols)}')
        ans.append(s)
        s = ""
        s = str(f'|{"":^{width}}| ')
        for symbol in self.parse_table_symbols:
            s = s + str(f'{symbol:^{width - 1}}| ')
        ans.append(s)

        print()
        print_line()
        s = ""
        for r in range(len(self.C)):
            s = s + str(f'|{r:^{width}}| ')

            for c in self.parse_table_symbols:
                s = s + str(f'{self.parse_table[r][c]:^{width - 1}}| ')
            ans.append(s)
            s = ""
            print()

        print_line()
        print()
        s = str(f'+{"-" * width}+{"-" * symbols_width(self.action)}+{"-" * symbols_width(self.goto)}+')
        ans.append(s)
        return ans
        files.close()

    def LR_parser(self, w):
        buffer = f'{w} $'.split()
        pointer = 0
        a = buffer[pointer]
        stack = ['0']
        symbols = ['']
        results = {'step': [''], 'stack': ['STACK'] + stack, 'symbols': ['SYMBOLS'] + symbols, 'input': ['INPUT'],
                   'action': ['ACTION']}

        step = 0
        while True:
            s = int(stack[-1])
            step += 1
            results['step'].append(f'({step})')
            results['input'].append(' '.join(buffer[pointer:]))

            if a not in self.parse_table[s]:
                results['action'].append(f'ERROR: unrecognized symbol {a}')

                break

            elif not self.parse_table[s][a]:
                results['action'].append('ERROR: input cannot be parsed by given grammar')

                break

            elif '/' in self.parse_table[s][a]:
                action = 'reduce' if self.parse_table[s][a].count('r') > 1 else 'shift'
                results['action'].append(f'ERROR: {action}-reduce conflict at state {s}, symbol {a}')

                break

            elif self.parse_table[s][a].startswith('s'):
                results['action'].append('shift')
                stack.append(self.parse_table[s][a][1:])
                symbols.append(a)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols))
                pointer += 1
                a = buffer[pointer]

            elif self.parse_table[s][a].startswith('r'):
                head, body = self.G_indexed[int(self.parse_table[s][a][1:])]
                results['action'].append(f'reduce by {head} -> {" ".join(body)}')

                if body != ('^',):
                    stack = stack[:-len(body)]
                    symbols = symbols[:-len(body)]

                stack.append(str(self.parse_table[int(stack[-1])][head]))
                symbols.append(head)
                results['stack'].append(' '.join(stack))
                results['symbols'].append(' '.join(symbols))

            elif self.parse_table[s][a] == 'acc':
                results['action'].append('accept')

                break

        return results

    def print_LR_parser(self, results):
        ans = []

        def print_line():
            ans.append(f'{"".join(["+" + ("-" * (max_len + 2)) for max_len in max_lens.values()])}+')

        max_lens = {key: max(len(value) for value in results[key]) for key in results}
        justs = {'step': '>', 'stack': '', 'symbols': '', 'input': '>', 'action': ''}

        print_line()
        ans.append(''.join(
            [f'| {history[0]:^{max_len}} ' for history, max_len in zip(results.values(), max_lens.values())]) + '|')
        print_line()
        for i, step in enumerate(results['step'][:-1], 1):
            ans.append(''.join([f'| {history[i]:{just}{max_len}} ' for history, just, max_len in
                                zip(results.values(), justs.values(), max_lens.values())]) + '|')

        ans.append(f'{"".join(["+" + ("-" * (max_len + 2)) for max_len in max_lens.values()])}+')
        return ans


def main(st):
    with open('grammar/5.txt') as grammar_file:

        G = Grammar(grammar_file.read())

        slr_parser = SLRParser(G)
        a = slr_parser.print_info()
        file = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\table.txt", 'w')
        for ele in a:
            file.write(ele + '\n')

        file.close()
        if len(st)>0:
            file = open("C:\\Users\\himanshu\\PycharmProjects\\pythonProject\\stack.txt", 'w')
            for i in st:
                r = slr_parser.LR_parser(str(i))
                a = slr_parser.print_LR_parser(r)
                for ele in a:
                    file.write(ele + '\n')
            file.close()

if __name__ == "__main__":
    main()