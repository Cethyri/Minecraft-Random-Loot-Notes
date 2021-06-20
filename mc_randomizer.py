import random
import sys
from typing import Optional

from mcr.flags import handleFlags
from mcr.gui import start_app
from mcr.mcr_data import MCRData

flags_info_and_seed = handleFlags(sys.argv[1:])

if flags_info_and_seed is None:
    sys.exit()

flags = flags_info_and_seed[0]
flagInfo = flags_info_and_seed[1]
seed: Optional[str] = flags_info_and_seed[2]

if seed is None:
    seed = str(random.randint(-sys.maxsize, sys.maxsize))

seed_generated = flags_info_and_seed[2] is None

datapack_name = 'mc_randomizer'

mcr_data: MCRData = MCRData(flags, flagInfo,
                           seed, seed_generated, datapack_name)

start_app(mcr_data)
