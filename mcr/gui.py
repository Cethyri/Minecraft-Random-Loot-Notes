import io
import os
import re
import threading
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from typing import Any, Callable, Optional
import zipfile

from idlelib.tooltip import Hovertip # type: ignore

from mcr.mcr_data import MCRData
import mcr.methods as methods


class Progress(tk.Toplevel):
    p_generation: ttk.Progressbar
    l_generationStep: ttk.Label
    l_generationDetail: ttk.Label

    stepVar: tk.StringVar
    detailVar: tk.StringVar

    def __init__(self, mcrData: MCRData, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.resizable(False, False)
        self.title('MCR Generation')
        self.iconphoto(False, tk.PhotoImage(file='Icon.png'))

        self.p_generation = ttk.Progressbar(
            self, length=250, value=0, maximum=methods.TOTAL_STEPS)
        self.p_generation.pack(padx=10, pady=10)

        self.stepVar = tk.StringVar(value='Loading...')
        self.l_generationStep = ttk.Label(self, textvariable=self.stepVar)
        self.l_generationStep.pack()

        self.detailVar = tk.StringVar(value='')
        self.l_generationDetail = ttk.Label(self, textvariable=self.detailVar)
        self.l_generationDetail.pack()

        mcrData.printStep = self.step
        mcrData.printDetail = self.detailVar.set

    def step(self, step: str, amount: Optional[int] = None):
        self.p_generation.step(amount)
        self.stepVar.set(step)

class FlagsFrame(ttk.Labelframe):
    cb_flags: dict[str, ttk.Checkbutton]

    mcrData: MCRData

    def __init__(self, mcrData: MCRData, flags: dict[str, tk.BooleanVar], handle_flag_change: Callable[[str], Any], *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)
        self.mcrData = mcrData

        self.grid(padx=10, pady=10, ipadx=10, ipady=10, sticky='nw', rowspan=2)

        self.cb_flags = {}
        for flag_name, value in mcrData.flags.items():
            flags[flag_name] = tk.BooleanVar(value=value)

            rb = ttk.Checkbutton(
                self,
                text=flag_name,
                variable=flags[flag_name],
                command=handle_flag_change(flag_name))
            rb.pack(expand=True, fill='both')

            self.cb_flags[flag_name] = rb

            if flag_name in mcrData.flagInfo:
                if 'hover' in mcrData.flagInfo[flag_name]:
                    Hovertip(rb, text=mcrData.flagInfo[flag_name]['hover'])
                elif 'explanation' in mcrData.flagInfo[flag_name]:
                    Hovertip(rb, text=mcrData.flagInfo[flag_name]['explanation'])

    def disable(self):
        for flag_name in self.cb_flags:
            self.cb_flags[flag_name].configure(state='disabled')


class InfoFrame(ttk.Labelframe):
    l_seed: ttk.Label
    e_seed: ttk.Entry

    l_datapack_name: ttk.Label
    e_datapackName: ttk.Entry

    def __init__(self, seed: tk.StringVar, datapackName: tk.StringVar, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.grid(padx=10, pady=10, sticky='ne', column=1, row=0)

        self.l_seed = ttk.Label(self, text='Seed:')
        self.l_seed.grid(sticky='sw')
        self.e_seed = ttk.Entry(
            self, textvariable=seed)
        self.e_seed.grid()

        self.l_datapack_name = ttk.Label(self, text='Datapack Name:')
        self.l_datapack_name.grid(sticky='sw')
        self.e_datapackName = ttk.Entry(
            self, textvariable=datapackName)
        self.e_datapackName.grid()

    def disable(self):
        self.e_seed.configure(state='disabled')
        self.e_datapackName.configure(state='disabled')


class Input(ttk.Frame):
    mcrData: MCRData

    # variables
    flags: dict[str, tk.BooleanVar]
    seed: tk.StringVar
    datapackName: tk.StringVar

    # subwidgets
    lf_flags: FlagsFrame

    lf_info: InfoFrame

    b_submit: ttk.Button

    tl_progress: Progress

    @property
    def fullName(self):
        seedPart = '' if self.mcrData.flags.hide_seed else f'(seed={self.seed.get()})'
        return self.datapackName.get() + seedPart

    def __init__(self, mcrData: MCRData, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.grid_rowconfigure(0, weight=1)  # type: ignore
        self.grid_columnconfigure(0, weight=1)  # type: ignore
        self.grid()

        self.mcrData = mcrData

        self.flags = {}
        self.seed = tk.StringVar(value=mcrData.seed)
        self.datapackName = tk.StringVar(value='mc_randomizer')

        self.seed.trace('w', self._handle_pack_name_change)
        self.datapackName.trace('w', self._handle_pack_name_change)

        self.lf_flags = FlagsFrame(
            mcrData, self.flags, self.handle_flag_change, master=self, text='Flags')

        self.lf_info = InfoFrame(
            self.seed, self.datapackName, master=self, text='Info')

        self.b_submit = ttk.Button(
            self, text="Submit", command=self._submit)
        self.b_submit.grid(padx=10, pady=10, column=1, row=1, sticky='se')

    def handle_flag_change(self, flag_name: str):
        def change_flag():
            self.mcrData.flags[flag_name] = self.flags[flag_name].get()
        return change_flag

    notAllowed: str = r'[^a-zA-Z\d_.-+]'

    def _handle_pack_name_change(self):
        self.seed.set(re.sub(self.notAllowed, '', self.seed.get()))

        self.datapackName.set(
            re.sub(self.notAllowed, '', self.datapackName.get()))

        self.mcrData.datapack_name = self.datapackName.get()
        self.mcrData.seed = self.seed.get()

    def _disableMainScreen(self):
        self.lf_flags.disable()
        self.lf_info.disable()
        self.b_submit.configure(state='disabled')

    def _submit(self):
        self._disableMainScreen()

        self._pickJar()

        self.tl_progress = Progress(self.mcrData)

        def start():
            methods.mc_randomizer(self.mcrData)

        threading.Thread(target=start).start()

    def _pickJar(self):
        if os.path.exists(methods.TEMP_DIR):
            for root, dirs, files in os.walk(methods.TEMP_DIR, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.removedirs(os.path.join(root, name))
            os.removedirs(methods.TEMP_DIR)

        os.makedirs(methods.TEMP_DIR)

        files = [('Jar Files', '*.jar')]
        appdata: str = os.getenv('APPDATA') or "%Appdata%"
        mc_path = os.path.join(appdata, '.minecraft', 'versions')

        jarpath: io.BufferedReader = filedialog.askopenfile(
            mode='r', filetypes=files, initialdir=mc_path)

        with zipfile.ZipFile(jarpath.name, 'r') as zip_:
            # zip_.extract('assets') # texture randomization, eh? You know you wanna!
            files = [n for n in zip_.namelist() if n.startswith('data/')]
            zip_.extractall(methods.TEMP_DIR, files)

    def _done(self):
        pass


class Setup(tk.Tk):
    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.resizable(False, False)
        self.title('MC Randomizer Setup')
        self.iconphoto(False, tk.PhotoImage(file='Icon.png'))


def start_app(mcrData: MCRData):
    root = Setup()
    # style: ttk.Style = ttk.Style(root)
    app = Input(
        mcrData,
        master=root
    )

    app.mainloop()
