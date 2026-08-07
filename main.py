class SephirahInterpreter:
    """Sephirah语言解释器"""
    
    class Stack:
        """一个栈。"""
        def __init__(self):
            self.stack = []
        def empty(self):
            return len(self.stack) == 0
        def push(self, obj):
            self.stack.append(obj)  
        def peek(self):
            return self.stack[-1]
        def pop(self):
            return self.stack.pop()
        def length(self):
            return len(self.stack)
        def print(self):
            print(self.stack)
        
    class SephirahRuntimeError(Exception):
        """Sephirah 解释器运行时发生的错误"""
        pass
    
    def __init__(self, codeLines):
        """
        初始化解释器
        
        Args:
            codeLines: 源代码行列表
        """
        self.codeLines = codeLines
        self.progLen = len(codeLines)
        self.instruction_map = {c: i for i, c in enumerate('0+^v()ga-n')}
        self.reset()
    
    def reset(self):
        """重置解释器状态"""
        self.progCnt = 0
        self.tape = [0]
        self.tapeIsSeph = [False]
        self.p = 0
        self.loopStack = self.Stack()
        self.outputBuffer = ''
    
    @staticmethod
    def i8_add(a, b):
        """有符号8位加法，自动溢出"""
        result = a + b
        result = result & 0xFF
        if result & 0x80:
            return result - 0x100
        return result
    
    @staticmethod
    def i8_sub(a, b):
        """有符号8位减法，自动下溢"""
        result = a - b
        result = result & 0xFF
        if result & 0x80:
            return result - 0x100
        return result
    
    def handle_new(self):
        """每次跳转到新的纸带格时检查该格是不是Sephirah，如果是则需要立即执行该Sephirah。"""
        if self.tapeIsSeph[self.p]:
            self.interpreter(self.tape[self.p] % 10)
    
    def interpreter(self, seph):
        """Sephirah指令的解释器。"""
        if seph == 0:
            pass
        
        elif seph == 1:
            if self.tapeIsSeph[self.p]:
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            self.tape[self.p] = self.i8_add(self.tape[self.p], 1)
                
        elif seph == 2:
            self.tapeIsSeph[self.p] = True
            
        elif seph == 3:
            self.tapeIsSeph[self.p] = False
            
        elif seph == 4:
            self.loopStack.push(self.progCnt)
            # self.loopStack.print()
            
        elif seph == 5:
            if self.tape[self.p] != 0:
                if self.loopStack.empty():
                    raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Sephirah ")" has nowhere to go.')
                else:
                    x = self.progCnt
                    # self.progCnt = self.loopStack.peek() - 1
                    # self.loopStack.pop()
                    # self.loopStack.print()
                    self.progCnt = self.loopStack.pop() - 1
                    # print(f"{x + 1} line ) to {self.progCnt + 1}")
                    # self.loopStack.print()
                    return
            else:
                if not self.loopStack.empty():
                    self.loopStack.pop()
                    
        elif seph == 6:
            if self.tapeIsSeph[self.p]:
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            else:
                steps = self.tape[self.p]
                if steps >= 0:
                    for _ in range(steps):
                        if self.p == len(self.tape) - 1:
                            self.tape.append(0)
                            self.tapeIsSeph.append(False)
                        self.p += 1
                else:
                    for _ in range(abs(steps)):
                        if self.p == 0:
                            self.tape.insert(0, 0)
                            self.tapeIsSeph.insert(0, False)
                        else:
                            self.p -= 1
                self.handle_new()
        
        elif seph == 7:
            if self.tapeIsSeph[self.p]:
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            try:
                char = chr(self.tape[self.p])
                self.outputBuffer += char
            except ValueError:
                pass
        
        elif seph == 8:
            if self.tapeIsSeph[self.p]:
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            if self.tape[self.p] > 0:
                if self.p == 0:
                    self.tape.insert(0, 0)
                    self.tapeIsSeph.insert(0, False)
                    self.p += 1
                self.tape[self.p - 1] = self.i8_sub(self.tape[self.p - 1], self.tape[self.p])
            else:
                if self.p == len(self.tape) - 1:
                    self.tape.append(0)
                    self.tapeIsSeph.append(False)
                self.tape[self.p + 1] = self.i8_sub(self.tape[self.p + 1], self.tape[self.p])
            self.tape[self.p] = 0
        
        elif seph == 9:
            if self.tapeIsSeph[self.p]:
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            self.tape[self.p] = self.i8_add(self.tape[self.p], len(self.tape))
            
        else:
            raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Undefined Sephirah number.')
    
    def createDebugLine(self, add=1):
        """创建一行调试信息"""
        debugLine = f'DEBUG: Line {(self.progCnt + add):04d} [ '
        for i in range(len(self.tape)):
            if self.tapeIsSeph[i]:
                debugLine += f'[{"0+^v()ga-n"[self.tape[i] % 10]}] '
            else:
                debugLine += f'{self.tape[i]:04d} '
        debugLine += f'] OUTPUT: {self.outputBuffer}\n'
        debugLine += '                 ' + '     ' * self.p + '   ^'
        return debugLine
    
    def run(self, debug=0, longTapeWarning=-1, mrkOnly = False):
        """
        运行Sephirah程序。
        
        Args:
            debug: 是否开启调试模式
            longTapeWarning: 纸带长度警告阈值，-1表示不检查
        """
        # 变量初始化
        self.reset()
        
        endByZero = None # 标志变量，检测程序是否因为遇到行中0而结束。
        tapeTooLong = False 
        
        debugLog = [] # 调试信息
        
        if debug > 0:
            if mrkOnly:
                print(f'===Running Sephirah code [DEBUG MODE - Mark Only] started===')
            else:
                print(f'===Running Sephirah code [DEBUG MODE] started===')
        else:
            print(f'===Running Sephirah code started===')
        
        if not mrkOnly and debug > 0:
            debugLine = self.createDebugLine()
            if debug < 3:
                    print(debugLine)
            if debug >= 2:
                debugLog.append(debugLine)
            
        while self.progCnt < self.progLen:
            line = self.codeLines[self.progCnt]
            
            if 'mrk' in line.lower() and debug > 0 and mrkOnly:
                debugLine = self.createDebugLine(add=0)
                if debug < 3:
                    print(debugLine)
                if debug >= 2:
                    debugLog.append(debugLine)
            
            if line[0] != '0':
                # 如果开头不是0则忽略本行
                self.progCnt += 1
                continue
            
            if line.count('.') + line.count('<') + line.count('>') != 1:
                # 如果没有移动指令就报错
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: This line has no or too many "." "<" or ">" command.')
            
            for i in range(len(line)):
                ch = line[i]
                
                if ch == '.':
                    # 点指令：原地移动
                    self.handle_new()
                
                elif ch == '<':
                    # 左移指令：向左移动一格
                    if self.p == 0:
                        self.tape.insert(0, 0)
                        self.tapeIsSeph.insert(0, False)
                    else:
                        self.p -= 1
                        self.handle_new()
                
                elif ch == '>':
                    # 右移指令：向右移动一格
                    if self.p == len(self.tape) - 1:
                        self.tape.append(0)
                        self.tapeIsSeph.append(False)
                        self.p += 1
                    else:
                        self.p += 1
                        self.handle_new()
                
                elif ch == '0':
                    if i == 0:
                        self.interpreter(0)
                    else:
                        endByZero = self.progCnt # 如果0在行中则停止运行程序
                        break 
                
                elif ch in '+^v()ga-n':
                    self.interpreter(self.instruction_map[ch])
                    
                elif ch == '\n' or ch == ' ':
                    pass
                
                elif ch == ';':
                    break
                
                else:
                    raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Undefined symbol "{ch}".')
            
            if not mrkOnly and debug > 0:
                debugLine = self.createDebugLine()
                if debug < 3:
                    print(debugLine)
                if debug >= 2:
                    debugLog.append(debugLine)
                
            if longTapeWarning >= 0 and len(self.tape) >= longTapeWarning:
                # print(len(self.tape))
                # raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: The tape is too long (more than {longTapeWarning} cells).')
                tapeTooLong = True
                break 
            
            if endByZero is not None:
                break
            
            self.progCnt += 1
            
        if self.outputBuffer != '' and not debug:
            print(self.outputBuffer)
        
        if endByZero is not None:
            print(f'===Running Sephirah code stopped by Sephirah "0" in Line {endByZero + 1}===')
        elif tapeTooLong:
            print(f'===Running Sephirah code stopped because the tape is too long (more than {longTapeWarning} cells)===')
        else:
            print('===Running Sephirah code finished===')
        
        if debug >= 2:
            with open('debug.log', 'w', encoding='utf-8') as file:
                file.write('\n'.join(debugLog))
            print('Debug log written into file "debug.log".')

if __name__ == "__main__":
    fileName = "code.seph"
    codeLines = None
    with open(fileName, 'r', encoding='utf-8') as file:
        codeLines = file.readlines()

    if codeLines is None:
        raise FileNotFoundError(f'Connot find Sephirah code file: "{FILENAME}".')

    debugmode = 0
    if 'debugout' in codeLines[0].lower():
        debugmode = 2
    elif 'debuglog' in codeLines[0].lower():
        debugmode = 3
    elif 'debug' in codeLines[0].lower():
        debugmode= 1
    
    if 'mrkonly' in codeLines[0].lower():
        mrkOnlyMode = True

    longTapeWarningMode = -1
    if 'ltw16' in codeLines[0].lower():
        longTapeWarningMode = 16
    elif 'ltw32' in codeLines[0].lower():
        longTapeWarningMode = 32
    elif 'ltw64' in codeLines[0].lower():
        longTapeWarningMode = 64
    elif 'ltw128' in codeLines[0].lower():
        longTapeWarningMode = 128
    elif 'ltw256' in codeLines[0].lower():
        longTapeWarningMode = 256
    elif 'ltw' in codeLines[0].lower():
        longTapeWarningMode = 64

    interp = SephirahInterpreter(codeLines)
    interp.run(debug=debugmode, longTapeWarning=longTapeWarningMode, mrkOnly = mrkOnlyMode)
