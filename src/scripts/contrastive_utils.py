"""
contrastive_utils.py
====================
Some tools for implementing contrastive learning.
"""

import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import Dataset

LARGE_NUMBER = 1e9


# --------------------------
# Dataset and Dataloader
class XPDataset(Dataset):
    def __init__(self, xp, xp_err):
        self.xp = torch.tensor(xp, dtype=torch.float32)
        self.xp_err = torch.tensor(xp_err, dtype=torch.float32)

    def __len__(self):
        return len(self.xp)

    def __getitem__(self, idx):
        return self.xp[idx], self.xp_err[idx]


# --------------------------
# Contrastive learning modules


class Augmentor(nn.Module):
    """
    Augmentor module
    Resamples based on the errors
    """

    def __init__(self, n_sigma=1):
        super().__init__()
        self.n_sigma = n_sigma  # Number of stdevs away from mean to go

    def forward(self, xp_batch, xp_err_batch):
        """
        Resample the xp coefficients.
        Assume uncorrelated Gaussian errors
        """
        mvn = torch.distributions.MultivariateNormal(
            xp_batch,  # Means
            torch.diag_embed(
                torch.square(xp_err_batch)
            ),  # Covariances (assumed diagonal)
        )

        return mvn.sample()  # (BATCH_SIZE, 110)


class Encoder(nn.Module):
    """
    Encoder module
    Generates a latent representation of the input
    """

    def __init__(self, n_hidden=(256, 128), n_out=64):
        super().__init__()
        self.architecture = nn.Sequential(
            nn.Linear(110, n_hidden[0]),
            nn.ReLU(),
            nn.Linear(n_hidden[0], n_hidden[1]),
            nn.ReLU(),
            nn.Linear(n_hidden[1], n_out),
        )

    def forward(self, x):
        return self.architecture(x)  # (BATCH_SIZE, n_out)


class Projector(nn.Module):
    """
    Projector module
    Generates encoded vector, on which contrastive loss applied
    """

    def __init__(self, n_in=64, n_hidden=32, n_out=16):
        # n_in should equal n_out of Encoder module before it
        super().__init__()
        self.architecture = nn.Sequential(
            nn.Linear(n_in, n_hidden), nn.ReLU(), nn.Linear(n_hidden, n_out)
        )

    def forward(self, x):
        return self.architecture(x)  # (BATCH_SIZE, n_out)


# --------------------------
# Full contrastive learning model


class Contrastor(nn.Module):
    """
    Full Contrastor module.
    Composed of an augmentor, encoder and projector.
    """

    def __init__(self, augmentor, encoder, projector, temp=1.0, batch_size=32):
        super().__init__()
        self.augmentor = augmentor
        self.encoder = encoder
        self.projector = projector
        self.temp = temp
        self.batch_size = batch_size

    def forward(self, xp_batch_, xp_err_batch_):
        x = self.augmentor(xp_batch_, xp_err_batch_)
        h = self.encoder(x)
        return self.projector(h)

    def compute_loss(self, xp_batch_, xp_err_batch_, temp=None, batch_size=None):
        """
        Computes the contrastive loss. Uses NT-Xent.
        """
        if batch_size is None:
            batch_size = self.batch_size
        if temp is None:
            temp = self.temp
        z1 = self.forward(xp_batch_, xp_err_batch_)  # (BATCH_SIZE, n_out)
        z2 = self.forward(xp_batch_, xp_err_batch_)  # (BATCH_SIZE, n_out)
        # z2 =/= z1 due to stochasticity in augmentor
        z = torch.cat([z1, z2])  # (2 * BATCH_SIZE, n_out)

        sim_matrix = torch.mm(F.normalize(z), F.normalize(z).t())
        # sim(z_i, z_j) = z_i.z_j / |z_i||z_j|
        sim_matrix.fill_diagonal_(-LARGE_NUMBER)  # To ignore z1.z1
        # | 0 . + . |
        # | . 0 . + | 0 = z_i.z_i
        # | + . 0 . | + = dot product between encodings of same xp spectrum, z_i.z_i*
        # | . + . 0 | . = " " " " different xp spectra

        rolled_matrix = torch.roll(sim_matrix, batch_size, 0)  # Translates down
        # | + . 0 . |
        # | . + . 0 | Now the positive pairs
        # | 0 . + . | are on the diagonal
        # | . 0 . + |

        # l_i = - log [ exp(sim(z_i, z_i*)/t) / Sum_(k=/=i) exp(sim(z_i, z_k)/t)
        positive_pairs = torch.diag(rolled_matrix / temp)
        negative_pairs = torch.logsumexp(rolled_matrix / temp, dim=0)

        return torch.mean(-positive_pairs + negative_pairs)
