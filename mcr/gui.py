import os
import re
import threading
import tkinter as tk
import tkinter.ttk as ttk
import zipfile
from tkinter import filedialog
from typing import Any, Callable, Optional

from idlelib.tooltip import Hovertip  # type: ignore

import mcr.methods as methods
from mcr.mcr_data import MCRData


class Progress(tk.Toplevel):
    p_generation: ttk.Progressbar
    l_generationStep: ttk.Label
    l_generationDetail: ttk.Label

    stepVar: tk.StringVar
    detailVar: tk.StringVar

    def __init__(self, mcr_data: MCRData, *args: Any, **kwargs: Any):

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

        mcr_data.printStep = self.step
        mcr_data.printDetail = self.detailVar.set

    def step(self, step: str, amount: Optional[int] = None):
        self.p_generation.step(amount)
        self.stepVar.set(step)


class FlagsFrame(ttk.Labelframe):
    cb_flags: dict[str, ttk.Checkbutton]

    mcr_data: MCRData

    def __init__(self, mcr_data: MCRData, flags: dict[str, tk.BooleanVar], handle_flag_change: Callable[[str], Any], *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)
        self.mcr_data = mcr_data

        self.grid(padx=10, pady=10, ipadx=10, ipady=10, sticky='nw', rowspan=2)

        self.cb_flags = {}
        for flag_name, value in mcr_data.flags.items():
            flags[flag_name] = tk.BooleanVar(value=value)

            rb = ttk.Checkbutton(
                self,
                text=flag_name,
                variable=flags[flag_name],
                command=handle_flag_change(flag_name))
            rb.pack(expand=True, fill='both')

            self.cb_flags[flag_name] = rb

            if flag_name in mcr_data.flagInfo:
                if 'hover' in mcr_data.flagInfo[flag_name]:
                    Hovertip(rb, text=mcr_data.flagInfo[flag_name]['hover'])
                elif 'explanation' in mcr_data.flagInfo[flag_name]:
                    Hovertip(
                        rb, text=mcr_data.flagInfo[flag_name]['explanation'])

    def disable(self):
        for flag_name in self.cb_flags:
            self.cb_flags[flag_name].configure(state='disabled')


class InfoFrame(ttk.Labelframe):
    l_seed: ttk.Label
    e_seed: ttk.Entry

    l_datapack_name: ttk.Label
    e_datapackName: ttk.Entry

    l_jar: ttk.Label
    cb_jar: ttk.Combobox

    def __init__(self, seed: tk.StringVar, datapackName: tk.StringVar, jarName: tk.StringVar, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.grid(padx=10, pady=10, column=1, row=0, sticky='ne')

        self.l_seed = ttk.Label(self, text='Seed:')
        self.l_seed.grid(sticky='sw')
        self.e_seed = ttk.Entry(
            self, textvariable=seed)
        self.e_seed.grid(sticky='sew')

        self.l_datapack_name = ttk.Label(self, text='Datapack Name:')
        self.l_datapack_name.grid(sticky='sw')
        self.e_datapackName = ttk.Entry(
            self, textvariable=datapackName)
        self.e_datapackName.grid(sticky='sew')


        jar_paths: list[str]
        if os.path.exists(methods.TEMP_DIR):
            jar_paths = list(os.path.relpath(p) for p in os.listdir(methods.TEMP_DIR))
        else:
            jar_paths = []

        self.l_jar = ttk.Label(self, text='Version:')
        self.l_jar.grid(sticky='sw')
        self.cb_jar = ttk.Combobox(
            self, textvariable=jarName, values=jar_paths)
        self.cb_jar.grid(sticky='sew')
        if len(jar_paths) == 0:
            jarName.set('Select...')
            self.cb_jar.configure(state='disabled')
        else:
            jarName.set(jar_paths[0])

    def disable(self):
        self.e_seed.configure(state='disabled')
        self.e_datapackName.configure(state='disabled')
        self.cb_jar.configure(state='disabled')


class Input(ttk.Frame):
    mcr_data: MCRData

    # variables
    flags: dict[str, tk.BooleanVar]
    seed: tk.StringVar
    datapackName: tk.StringVar
    jarName: tk.StringVar

    # subwidgets
    lf_flags: FlagsFrame

    lf_info: InfoFrame

    b_submit: ttk.Button

    tl_progress: Progress

    @property
    def fullName(self):
        seedPart = '' if self.mcr_data.flags.hide_seed else f'(seed={self.seed.get()})'
        return self.datapackName.get() + seedPart

    def __init__(self, mcr_data: MCRData, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.grid_rowconfigure(0, weight=1)  # type: ignore
        self.grid_columnconfigure(0, weight=1)  # type: ignore
        self.grid()

        self.mcr_data = mcr_data

        self.flags = {}
        self.seed = tk.StringVar(value=mcr_data.seed)
        self.datapackName = tk.StringVar(value='mc_randomizer')
        self.jarName = tk.StringVar(value='')

        self.seed.trace('w', self._handle_pack_name_change)
        self.datapackName.trace('w', self._handle_pack_name_change)

        self.lf_flags = FlagsFrame(
            mcr_data, self.flags, self.handle_flag_change, master=self, text='Flags')

        self.lf_info = InfoFrame(
            self.seed, self.datapackName, self.jarName, master=self, text='Info')

        self.b_submit = ttk.Button(
            self, text="Submit", command=self._submit)
        self.b_submit.grid(padx=10, pady=10, column=1, row=1, sticky='ne')

    def handle_flag_change(self, flag_name: str):
        def change_flag():
            self.mcr_data.flags[flag_name] = self.flags[flag_name].get()
        return change_flag

    notAllowed: str = r'[^a-zA-Z\d_.-+]'

    def _handle_pack_name_change(self):
        self.seed.set(re.sub(self.notAllowed, '', self.seed.get()))

        self.datapackName.set(
            re.sub(self.notAllowed, '', self.datapackName.get()))

        self.mcr_data.datapack_name = self.datapackName.get()
        self.mcr_data.seed = self.seed.get()

    def _disableMainScreen(self):
        self.lf_flags.disable()
        self.lf_info.disable()
        self.b_submit.configure(state='disabled')

    def _submit(self):
        self._disableMainScreen()

        self.tl_progress = Progress(self.mcr_data)
        self.tl_progress.transient(self) # type: ignore

        def start():
            self._pickJar()
            self.tl_progress.focus()
            methods.mc_randomizer(self.mcr_data)

        threading.Thread(target=start).start()

    def _pickJar(self):

        self.tl_progress.step('Selecting Minecraft Jar File', 0)

        if not os.path.exists(methods.TEMP_DIR):
            os.makedirs(methods.TEMP_DIR)

        jarpath = os.path.join(methods.TEMP_DIR, self.jarName.get())
        jarname = os.path.basename(jarpath)

        while not os.path.exists(jarpath) or jarpath == '':
            files = [('Jar Files', '*.jar')]
            appdata: str = os.getenv('APPDATA') or "%Appdata%"
            mc_path = os.path.join(appdata, '.minecraft', 'versions')

            jarpath = filedialog.askopenfilename(filetypes=files, initialdir=mc_path)
            jarname = os.path.basename(jarpath).replace('.jar', '')

            with zipfile.ZipFile(jarpath, 'r') as zip_:
                # zip_.extract('assets') # texture randomization, eh? You know you wanna!
                files = [n for n in zip_.namelist() if n.startswith('data/')]
                zip_.extractall(os.path.join(methods.TEMP_DIR, jarname), files)
        
        self.mcr_data.jarname = jarname

    def _done(self):
        pass


class Setup(tk.Tk):
    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

        self.resizable(False, False)
        self.title('MC Randomizer Setup')
        self.iconphoto(False, tk.PhotoImage(file='Icon.png'))


def start_app(mcr_data: MCRData):
    root = Setup()
    # style: ttk.Style = ttk.Style(root)
    app = Input(
        mcr_data,
        master=root
    )

    app.mainloop()
