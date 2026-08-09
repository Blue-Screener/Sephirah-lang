class SephirahInterpreter:
    """Sephirah语言解释器"""
    
    SEPH_MAP = {c: i for i, c in enumerate('0+^v()ga-n')} # Sephirah的字典
    
    
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
    
    
    class RuntimeOptions:
        """运行选项"""
        def __init__(self, line=None, debug=False, printOut=False, log=False, mrkOnly=False, ltw=-1):
            self.debug = debug # 是否生成调试信息
            self.printOut = printOut # 是否将调试信息输出至控制台
            self.log = log # 是否储存到文件
            self.mrkOnly = mrkOnly # 是否仅在mrk处输出调试信息
            self.ltw = ltw # 长纸带警告阈值（-1表示关闭）
            
            self.logName = "debug.log"
            
            if line is not None:
                self.parser(line)
        
        def parser(self, line, defaultLtw=64):
            line = line.lower()
            
            if 'debug' in line:
                self.debug = True 
                if 'debugout' in line:
                    self.printOut = True
                    self.log = True
                elif 'debuglog' in line:
                    self.log = True
                else:
                    self.printOut = True
            
            if 'mrkonly' in line:
                self.mrkOnly = True 
            
            if 'ltw' in line:
                if 'ltw16' in line:
                    self.ltw = 16
                elif 'ltw32' in line:
                    self.ltw = 32
                elif 'ltw64' in line:
                    self.ltw = 64
                elif 'ltw128' in line:
                    self.ltw = 128
                elif 'ltw256' in line:
                    self.ltw = 256
                else:
                    self.ltw = defaultLtw
    
    
    class SephirahRuntimeError(Exception):
        """Sephirah 解释器运行时发生的错误"""
        pass
    
    
    def __init__(self, codeLines):
        """初始化解释器"""
        self.codeLines = codeLines
        self.progLen = len(codeLines)
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
    
    
    def tapeLength(self):
        """返回纸带长度"""
        return len(self.tape)
    
    
    def getCell(self, d=0):
        """返回单元格内的数值，0代表当前格，-1代表左侧格，1代表右侧格"""
        if d <= -2 or d >= 2:
            raise ValueError("getCell() can only accept -1, 0, or 1")
        
        if d == -1 and self.p == 0:
            self.createLeft()
        if d == 1 and self.p == self.tapeLength() - 1:
            self.createRight()
        
        return self.tape[self.p + d]
    
    def getCellIsSeph(self, d=0):
        """返回单元格内是不是Sephirah，0代表当前格，-1代表左侧格，1代表右侧格"""
        if d <= -2 or d >= 2:
            raise ValueError("getCellIsSeph() can only accept -1, 0, or 1")
        
        if d == -1 and self.p == 0:
            self.createLeft()
        if d == 1 and self.p == self.tapeLength() - 1:
            self.createRight()
        
        return self.tapeIsSeph[self.p + d]
    
    def setCell(self, val, d=0):
        """设置当前单元格的值，0代表当前格，-1代表左侧格，1代表右侧格"""
        if d <= -2 or d >= 2:
            raise ValueError("setCell() can only accept -1, 0, or 1")
        
        if d == -1 and self.p == 0:
            self.createLeft()
        if d == 1 and self.p == self.tapeLength() - 1:
            self.createRight()
        
        self.tape[self.p + d] = val
    
    def setCellIsSeph(self, val):
        """设置当前单元格是否为Sephirah"""
        self.tapeIsSeph[self.p] = val
    
    
    def createLeft(self, initVal=0, isSeph=False):
        """在左侧创建新单元格，同时指针不动"""
        self.tape.insert(0, initVal)
        self.tapeIsSeph.insert(0, isSeph)
        self.p += 1
        
    def createRight(self, initVal=0, isSeph=False):
        """在右侧创建新单元格，同时指针不动"""
        self.tape.append(initVal)
        self.tapeIsSeph.append(isSeph)
        
    def moveLeft(self):
        """指针向左移动1格"""
        if self.p == 0:
            self.createLeft()
        self.p -= 1
    
    def moveRight(self):
        """指针向右移动1格"""
        if self.p == self.tapeLength() - 1:
            self.createRight()
        self.p += 1
    
    
    def handleNew(self):
        """每次跳转到新的纸带格时检查该格是不是Sephirah，如果是则需要立即执行该Sephirah。"""
        if self.getCellIsSeph():
            self.interpreter(self.getCell() % 10)
    
    
    def interpreter(self, seph):
        """Sephirah指令的解释器。"""
        if seph == 0: # 0
            pass
        
        elif seph == 1: # +
            if self.getCellIsSeph():
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            self.setCell(self.i8_add(self.getCell(), 1))
                
        elif seph == 2: # ^
            self.setCellIsSeph(True)
            
        elif seph == 3: # v
            self.setCellIsSeph(False)
            
        elif seph == 4: # (
            self.loopStack.push(self.progCnt)
            
        elif seph == 5: # )
            if self.getCell() != 0:
                if self.loopStack.empty():
                    raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Sephirah ")" has nowhere to go.')
                else:
                    self.progCnt = self.loopStack.pop() - 1
            else:
                if not self.loopStack.empty():
                    self.loopStack.pop()
                    
        elif seph == 6: # g
            if self.getCellIsSeph():
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            else:
                steps = self.getCell()
                if steps >= 0:
                    for _ in range(steps):
                        self.moveRight()
                else:
                    for _ in range(abs(steps)):
                        self.moveLeft()
                self.handleNew()
        
        elif seph == 7: # a
            if self.getCellIsSeph():
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            try:
                self.outputBuffer += chr(self.getCell())
            except ValueError:
                pass
        
        elif seph == 8: # -
            if self.getCellIsSeph():
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            if self.getCell() > 0:
                self.setCell(self.i8_sub(self.getCell(-1), self.getCell()), d=-1)
            else:
                self.setCell(self.i8_sub(self.getCell(1), self.getCell()), d=1)
            self.setCell(0)
        
        elif seph == 9: # n
            if self.getCellIsSeph():
                raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Expected a number instead of a Sephirah.')
            self.setCell(self.i8_add(self.getCell(), self.tapeLength()))
            
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
    
    
    def run(self):
        """
        运行Sephirah程序。
        """
        # 变量初始化
        self.reset()
        
        endByZero = None # 标志变量，检测程序是否因为遇到行中0而结束。
        tapeTooLong = False # 标志变量，检测程序是否因为长纸带警报而结束。
        
        runOp = self.RuntimeOptions(self.codeLines[0]) # 运行选项
        
        debugLog = [] # 调试信息
        
        if runOp.debug:
            if runOp.mrkOnly:
                print(f'===Running Sephirah code [DEBUG MODE - Mark Only] started===')
            else:
                print(f'===Running Sephirah code [DEBUG MODE] started===')
        else:
            print(f'===Running Sephirah code started===')
        
        if runOp.debug and (not runOp.mrkOnly):
            debugLine = self.createDebugLine(add=0)
            if runOp.printOut:
                    print(debugLine)
            if runOp.log:
                debugLog.append(debugLine)
            
        while self.progCnt < self.progLen:
            line = self.codeLines[self.progCnt]
            
            if ('mrk' in line.lower()) and runOp.debug and runOp.mrkOnly:
                debugLine = self.createDebugLine()
                if runOp.printOut:
                    print(debugLine)
                if runOp.log:
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
                    self.handleNew()
                
                elif ch == '<':
                    # 左移指令：向左移动一格
                    self.moveLeft()
                    self.handleNew()
                
                elif ch == '>':
                    # 右移指令：向右移动一格
                    self.moveRight()
                    self.handleNew()
                
                elif ch == '0':
                    if i == 0:
                        self.interpreter(0)
                    else:
                        endByZero = self.progCnt # 如果0在行中则停止运行程序
                        break 
                
                elif ch in '+^v()ga-n':
                    self.interpreter(self.SEPH_MAP[ch])
                    
                elif ch == '\n' or ch == ' ':
                    pass
                
                elif ch == ';':
                    break
                
                else:
                    raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: Undefined symbol "{ch}".')
            
            if runOp.debug and (not runOp.mrkOnly):
                debugLine = self.createDebugLine()
                if runOp.printOut:
                    print(debugLine)
                if runOp.log:
                    debugLog.append(debugLine)
                
            if runOp.ltw >= 0 and self.tapeLength() >= runOp.ltw:
                # raise self.SephirahRuntimeError(f'Error running Sephirah code, line {self.progCnt + 1}: The tape is too long (more than {ltw} cells).')
                tapeTooLong = True
                break 
            
            if endByZero is not None:
                break
            
            self.progCnt += 1
            
        if self.outputBuffer != '' and (not runOp.debug):
            print(self.outputBuffer)
        
        if endByZero is not None:
            print(f'===Running Sephirah code stopped by Sephirah "0" in Line {endByZero + 1}===')
        elif tapeTooLong:
            print(f'===Running Sephirah code stopped because the tape is too long (more than {runOp.ltw} cells)===')
        else:
            print('===Running Sephirah code finished===')
        
        if runOp.log:
            with open(runOp.logName, 'w', encoding='utf-8') as file:
                file.write('\n'.join(debugLog))
            print(f'Debug log written into file "{runOp.logName}".')


if __name__ == "__main__":
    fileName = "code.seph"
    codeLines = None
    with open(fileName, 'r', encoding='utf-8') as file:
        codeLines = file.readlines()

    if codeLines is None:
        raise FileNotFoundError(f'Connot find Sephirah code file: "{fileName}".')

    interp = SephirahInterpreter(codeLines)
    interp.run()
