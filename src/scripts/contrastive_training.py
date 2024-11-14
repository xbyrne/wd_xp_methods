"""
contrastive_training.py
=======================
Trains contrastive learning model
"""

from tqdm import tqdm
import numpy as np
import torch
from accelerate import Accelerator

# import preprocessors as pp
import contrastive_utils as cutils

# Constants & hyperparameters
BATCH_SIZE = 32
LR = 3e-4
N_EPOCHS = 100

# Load the data
fl = np.load("../data/interim/xp_coeffs.npz")
ids = fl["ids"]
xp = fl["xp"]
xp_err = fl["xp_err"]

# Preprocessing?
# xp = pp.divide_Gflux(xp, ids)
# xp_err = pp.divide_Gflux(xp_err, ids)

full_dataset = torch.tensor(xp, dtype=torch.float32)
dataloader = torch.utils.data.DataLoader(
    full_dataset, batch_size=BATCH_SIZE, shuffle=True
)

# Set up model
contrastor = cutils.Contrastor(
    cutils.Augmentor(n_sigma=1),
    cutils.Encoder(n_hidden=(256, 128), n_out=64),
    cutils.Projector(n_hidden=(256, 128), n_out=64),
    temp=1.0,
    batch_size=BATCH_SIZE,
)

# Compile model
optimiser = torch.optim.Adam(contrastor.parameters(), lr=LR)

# Accelerating
accelerator = Accelerator()
contrastor, optimiser, dataloader = accelerator.prepare(
    contrastor, optimiser, dataloader
)
contrastor.train()

# Training loop
losses = []
for epoch in tqdm(range(N_EPOCHS)):
    pbar = tqdm(dataloader)
    for batch in pbar:
        optimiser.zero_grad()
        loss = contrastor(batch)
        loss.backward()
        optimiser.step()
        losses.append(loss.item())
        pbar.set_description(f"Loss: {loss.item()}")
