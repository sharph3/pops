def parse_line(line):
    line = line.strip()
    line = line.replace('\t', ' ')
    line = line.replace('{', ' { ')
    line = line.replace('}', ' } ')
    line = line.replace('[', ' [ ')
    line = line.replace(']', ' ] ')
    line = line.replace('=', ' = ')
    line = line.replace('>', ' > ')
    line = line.replace('<', ' < ')

    while '  ' in line:
        line = line.replace('  ', ' ')

    line = line.replace('> =', '>=')
    line = line.replace('< =', '<=')
    line = line.replace('= =', '==')

    comma = False
    comment = False

    for i, char in enumerate(line):
        if char == '#':
            if not comma:
                line = line[:i]
                
                break
        elif char == '"':
            if comma:
                comma = False
            else:
                comma = True
        elif char == ' ':
            if comma:
                line = line[:i] + '%' + line[i + 1:]

    line = line.strip()

    prev = 0
    
    while True:
        start = line.find('[ [', prev)

        if start + 1:
            end = line.find(']', start)
            block = line[start:end + 1]
            block_new = block.replace(' ', '')
            line = line.replace(block, block_new)
            prev = start + len(block_new)
        else:
            break

    if line:
        tokens = line.split(' ')
        tokens = [token.replace('%', ' ') for token in tokens]

        return tokens
    else:
        return []
    

def parse_file(path):
    with open(path, encoding='utf-8-sig') as f:
        file = list()
        stack = [file]

        for line in f.readlines():
            rhs = False
            
            for token in parse_line(line):
                if token == '=':
                    rhs = True
                    
                    stack[-1][-1] = [stack[-1][-1]]
                    stack.append(stack[-1][-1])
                elif token == '{':
                    rhs = False
                    
                    stack[-1].append(list())
                    stack.append(stack.pop()[-1])
                elif token == '}' or token == ']':
                    stack.pop()
                elif '[[' in token:
                    stack[-1].append([token[1:], list()])
                    stack.append(stack[-1][-1][1])
                elif token == '>' or token == '<' or token == '>=' or token == '<=' or token == '==':
                    rhs = True

                    stack[-1][-1] = [stack[-1][-1], token]
                    stack.append(stack[-1][-1])
                else:
                    stack[-1].append(token)

                    if rhs:
                        rhs = False

                        stack.pop()

        return file

def apply_script(file, scripts, check=[False]):
    out = list()

    for f in file:
        if f[0] in scripts:
            check[0] = True
            
            if f[1] == 'yes':
                out.extend(apply_paras(scripts[f[0]], []))
            elif f[1] == 'no':
                out.append(['NOT', apply_paras(scripts[f[0]], [])])
            else:
                out.extend(apply_paras(scripts[f[0]], f[1]))
        elif type(f[1]) != type(list()) or not f[1] or type(f[1][0]) != type(list()):
            out.append(f)
        else:
            out.append([f[0], apply_script(f[1], scripts, check)])
            
    return out

def apply_paras(script, paras):
    out = list()

    for section in script:
        if '[' in section[0]:
            for para in paras:
                if section[0][1:-1] == para[0]:
                    out.extend(apply_paras(section[1], paras))

                    break
        else:
            foo = str(section[0])

            if '$' in foo:
                for para in paras:
                    foo = foo.replace(f'${para[0]}$', para[1])
                    
            if type(section[1]) == type(list()):
                out.append([foo, apply_paras(section[1], paras)])
            elif '$' in section[1]:
                bar = str(section[1])

                for para in paras:
                    bar = bar.replace(f'${para[0]}$', para[1])

                out.append([foo, bar])
            else:
                out.append([foo, str(section[1])])
                
    return out

def reconstruct(file, t=''):
    txt = ''

    for f in file:
        if f:
            try:
                f[1]
            except:
                print(f)
            if type(f[1]) == type(list()):
                txt += '%s%s = {' % (t, f[0])

                if not f[1]:
                    txt += '}\n'
                elif type(f[1][0]) != type(list()):
                    for item in f[1]:
                        txt += ' %s' % item
                    txt += ' }\n'
                else:
                    txt += '\n%s%s}\n' % (reconstruct(f[1], t + '\t'), t)
            elif len(f) == 3 and type(f[0]) != type(list()) and type(f[1]) != type(list()) and type(f[2]) != type(list()):
                txt += '%s%s %s %s\n' % (t, f[0], f[1], f[2])
            else:
                txt += '%s%s = %s\n' % (t, f[0], f[1])

    return txt
            
            
if __name__ == '__main__':
    import glob

    for path in glob.glob('common\\decisions\\*.txt'):
        file = parse_file(path)

        for block in file:
            block = block[1]

            if type(block) == type(list()):
                has_entry = False
                
                for entry in block:
                    if entry[0] == 'is_shown':
                        has_entry = True

                        new_entry = [['is_character', 'yes']]
                        new_entry.extend(entry[1])

                        entry[1] = new_entry

                        break

                if not has_entry:
                    block.append(['is_shown', [['is_character', 'yes']]])

        with open('foo\\%s' % path.split('\\')[-1], 'w') as f:
            f.write(reconstruct(file))
