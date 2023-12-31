# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_rnn.ipynb.

# %% auto 0
__all__ = ['SequentialDataset', 'VerticalSampler', 'multi_output_cross_entropy', 'HiddenStateResetterS']

# %% ../nbs/06_rnn.ipynb 2
import random
from functools import reduce, partial
from pathlib import Path
from urllib.request import urlretrieve
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import torcheval.metrics as tem
import fastcore.all as fc

from .dataloaders import DataLoaders
from .learner import *
from .activations import *
from .acceleration import *

# %% ../nbs/06_rnn.ipynb 3
class SequentialDataset():
    def __init__(self, lines, c2i, sequence_length):
        text = "." + ".".join(lines) + "."
        self.x = []
        self.y = []
        for i in range(0, len(text) - sequence_length - 1, sequence_length):
            self.x.append([c2i[xi] for xi in text[i: i+sequence_length]])
            self.y.append([c2i[yi] for yi in text[i+1: i+sequence_length+1]])
        self.x = torch.tensor(self.x)
        self.y = torch.tensor(self.y)
    
    def __getitem__(self, i):
        return self.x[i], self.y[i]

    def __len__(self):
        return len(self.x)

# %% ../nbs/06_rnn.ipynb 4
class VerticalSampler():
    def __init__(self, ds, batch_size):
        self.batch_size = batch_size
        self.batches = len(ds) // self.batch_size
        
    def __iter__(self):
        for i in range(self.batches):
            for j in range(self.batch_size):
                yield i + self.batches*j
                
    def __len__(self):
        return self.batches * self.batch_size

# %% ../nbs/06_rnn.ipynb 5
def multi_output_cross_entropy(logits, targets):
    # logits = [bs, context_length, output_classes]
    # targets = [bs, context_length]
    
    targets = targets.view(-1)
    
    bs, context_length, output_classes = logits.shape
    logits = logits.view(-1, output_classes)
    
    return F.cross_entropy(logits, targets)

# %% ../nbs/06_rnn.ipynb 6
class HiddenStateResetterS(Subscriber):
    def before_epoch(self, learn):
        learn.model.reset_hidden_state()
