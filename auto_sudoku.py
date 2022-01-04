import tkinter as tk
import numpy as np
import time
from copy import deepcopy as dc


def trying(var):
    try:
        var = int(var)
    except ValueError:
        var = 0
    return var


def str_to_lst(string):
    result = []
    for i in string:
        try:
            i = int(i)
            result += [i]
        except ValueError:
            pass
    return result


def un_list(arr):
    result = []
    for word in arr:
        if type(word) == int:
            result += [word]
        elif type(word) == list:
            result += un_list(word)
        else:
            word = str(word)
            result += word
    return result


block_dict = {1: ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)),
              2: ((1, 4), (1, 5), (1, 6), (2, 4), (2, 5), (2, 6), (3, 4), (3, 5), (3, 6)),
              3: ((1, 7), (1, 8), (1, 9), (2, 7), (2, 8), (2, 9), (3, 7), (3, 8), (3, 9)),
              4: ((4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (6, 1), (6, 2), (6, 3)),
              5: ((4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 4), (6, 5), (6, 6)),
              6: ((4, 7), (4, 8), (4, 9), (5, 7), (5, 8), (5, 9), (6, 7), (6, 8), (6, 9)),
              7: ((7, 1), (7, 2), (7, 3), (8, 1), (8, 2), (8, 3), (9, 1), (9, 2), (9, 3)),
              8: ((7, 4), (7, 5), (7, 6), (8, 4), (8, 5), (8, 6), (9, 4), (9, 5), (9, 6)),
              9: ((7, 7), (7, 8), (7, 9), (8, 7), (8, 8), (8, 9), (9, 7), (9, 8), (9, 9))}
block4_dict = {1: ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4), (4, 2), (4, 3), (4, 4)),
               2: ((2, 6), (2, 7), (2, 8), (3, 6), (3, 7), (3, 8), (4, 6), (4, 7), (4, 8)),
               3: ((6, 2), (6, 3), (6, 4), (7, 2), (7, 3), (7, 4), (8, 2), (8, 3), (8, 4)),
               4: ((6, 6), (6, 7), (6, 8), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8))}


class Field(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        self.master.title('SudokuSolver v3.0')
        self.num_range = (1, 2, 3, 4, 5, 6, 7, 8, 9)
        self.field = list(np.arange(81))
        self.hints = list(np.arange(81))
        self.field_rows = [[], [], [], [], [], [], [], [], []]
        self.field_cols = [[], [], [], [], [], [], [], [], []]
        self.field_blocks = [[], [], [], [], [], [], [], [], []]
        self.field_subs = [[], [], [], []]
        self.hint_rows = [[], [], [], [], [], [], [], [], []]
        self.hint_cols = [[], [], [], [], [], [], [], [], []]
        self.hint_blocks = [[], [], [], [], [], [], [], [], []]
        self.hint_subs = [[], [], [], []]
        self.chb_var = tk.IntVar()
        self.define_widgets()
        self.grid()

    def define_widgets(self):
        for i in range(81):
            row, col = (i // 9 + 1, i % 9 + 1)
            self.field[i] = [Cell(row, col), tk.Entry(self)]
            self.hints[i] = [Hint(row, col), tk.Label(self)]
        for elem in self.field:
            info, cell = elem
            row, col, block = info.row, info.col, info.block
            if info.block4:
                self.field_subs[info.block4 - 1] += [elem]
            cell['width'] = 3
            cell['justify'] = tk.CENTER
            cell['textvariable'] = info.var
            info.var.set('')
            self.field_rows[row - 1] += [elem]
            self.field_cols[col - 1] += [elem]
            self.field_blocks[block - 1] += [elem]
            cell.grid(row=row, column=col)
        for elem in self.hints:
            info, cell = elem
            row, col, block = info.row, info.col, info.block
            if info.block4:
                self.hint_subs[info.block4 - 1] += [elem]
            cell['width'] = 10
            cell['justify'] = tk.CENTER
            cell['textvariable'] = info.var
            self.hint_rows[row - 1] += [elem]
            self.hint_cols[col - 11] += [elem]
            self.hint_blocks[block - 1] += [elem]
            cell.grid(row=row, column=col)

        btn_clear = tk.Button(self, text='Clear')
        btn_clear['command'] = self.clear
        btn_clear.grid(row=1, column=0, rowspan=2, sticky=tk.EW)

        btn_comp = tk.Button(self, text='Compute')
        btn_comp['command'] = self.compute
        btn_comp.grid(row=3, column=0, rowspan=2, sticky=tk.EW)

        chb_extra = tk.Checkbutton(self, text='Extra?')
        chb_extra['variable'] = self.chb_var
        chb_extra.grid(row=5, column=0, rowspan=2)

        btn_auto = tk.Button(self, text='Autocomplete')
        btn_auto['command'] = self.auto_solve
        btn_auto.grid(row=7, column=0, rowspan=2)
        self.layout()

    def compute(self):
        self.layout()
        for i in range(len(self.field)):
            f_info, f_cell = self.field[i]
            f_var = trying(f_info.var.get())
            h_info, h_cell = self.hints[i]
            if f_var in self.num_range:
                result = ''
            else:
                result = self.possibilities(f_info)
            h_info.var.set(result)
        # optimize hints list
        items = [self.hint_rows, self.hint_cols, self.hint_blocks]
        for item in items:
            for row in item:
                lst = []
                for cell in row:
                    info, item = cell
                    val = str_to_lst(info.var.get())
                    lst.append(val)
                lst = self.optimize(lst)
                for i in range(len(row)):
                    info, item = row[i]
                    info.var.set(lst[i])
        if self.chb_var.get():
            for block in self.hint_subs:
                lst = []
                for cell in block:
                    info, item = cell
                    val = str_to_lst(info.var.get())
                    lst.append(val)
                lst = self.optimize(lst)
                for i in range(len(block)):
                    info, item = block[i]
                    info.var.set(lst[i])

    def possibilities(self, cell):
        result = list(self.num_range)
        i, j, k = cell.row - 1, cell.col - 1, cell.block - 1
        items = [self.field_rows[i], self.field_cols[j], self.field_blocks[k]]
        for series in items:
            for elem in series:
                info, item = elem
                var = trying(info.var.get())
                if var in result:
                    result.remove(var)
        if self.chb_var.get() and cell.block4:
            for elem in self.field_subs[cell.block4 - 1]:
                info, item = elem
                var = trying(info.var.get())
                if var in result:
                    result.remove(var)
        return result

    def optimize(self, arr):
        result = []
        indexes = []
        ret_list = dc(arr)
        for i in range(len(arr)):
            for j in range(len(arr)):
                if arr[i] == arr[j] and i != j and arr[i] not in result and len(arr[i]) == 2:
                    result.append(arr[i])
                    indexes.append(i)
                    indexes.append(j)
        result = un_list(result)
        for k in range(len(arr)):
            for l in range(len(arr[k])):
                elem = arr[k][l]
                if elem in result and k not in indexes:
                    ret_list[k].remove(elem)
        arr = un_list(dc(ret_list))
        for num in self.num_range:
            if arr.count(num) == 1:
                for i in range(len(ret_list)):
                    if type(ret_list[i]) not in (list, tuple):
                        ret_list[i] = [ret_list[i]]
                    if num in ret_list[i]:
                        ret_list[i] = [num]
        return ret_list

    def auto_solve1(self):
        self.compute()
        for i in range(len(self.hints)):
            h_info, h_item = self.hints[i]
            val = str_to_lst(h_info.var.get())
            if len(val) == 1:
                f_info, f_item = self.field[i]
                f_info.var.set(str(val[0]))
        self.compute()

    def auto_solve(self):
        t0 = time.time()
        start = True
        while start:
            self.auto_solve1()
            count = 0
            for elem in self.hints:
                h_info, h_item = elem
                val = str_to_lst(h_info.var.get())
                if len(val) == 1:
                    count += 1
            if count == 0:
                start = False
        print(time.time()-t0)

    def clear(self):
        self.layout()
        for elem in self.field:
            info, cell = elem
            info.var.set('')
        for elem in self.hints:
            info, cell = elem
            info.var.set(self.num_range)

    def layout(self):
        if self.chb_var.get():
            for cell in self.field:
                info, item = cell
                item['bg'] = 'white'
            for i in range(len(self.field_subs)):
                for cell in self.field_subs[i]:
                    info, item = cell
                    item['bg'] = 'lightgrey'
            for cell in self.hints:
                info, item = cell
                item['bg'] = 'white'
            for i in range(len(self.hint_subs)):
                for cell in self.hint_subs[i]:
                    info, item = cell
                    item['bg'] = 'lightgrey'
        else:
            for i in range(len(self.field_blocks)):
                for cell in self.field_blocks[i]:
                    info, item = cell
                    if i % 2 == 1:
                        item['bg'] = 'lightgrey'
                    else:
                        item['bg'] = 'white'
            for i in range(len(self.hint_blocks)):
                for cell in self.hint_blocks[i]:
                    info, item = cell
                    if i % 2 == 1:
                        item['bg'] = 'lightgrey'
                    else:
                        item['bg'] = 'white'


class Cell:
    def __init__(self, row=1, col=1):
        self.row = row
        self.col = col
        for i in block_dict:
            if (row, col) in block_dict[i]:
                self.block = i
        j = 1
        self.block4 = False
        while not self.block4 and j < 5:
            try:
                if (row, col) in block4_dict[j]:
                    self.block4 = j
            except KeyError:
                pass
            j += 1
        self.var = tk.StringVar()


class Hint:
    def __init__(self, row=1, col=1):
        self.row = row
        self.col = col + 10
        for i in block_dict:
            if (row, col) in block_dict[i]:
                self.block = i
        j = 1
        self.block4 = False
        while not self.block4 and j < 5:
            try:
                if (row, col) in block4_dict[j]:
                    self.block4 = j
            except KeyError:
                pass
            j += 1
        self.var = tk.StringVar()


my_Gui = Field()
my_Gui.mainloop()
