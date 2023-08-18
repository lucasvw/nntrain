# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_dataloaders.ipynb.

# %% auto 0
__all__ = ['hf_ds_collate_fn', 'DataLoaders']

# %% ../nbs/01_dataloaders.ipynb 2
from functools import partial

import torchvision.transforms.functional as TF
from torch.utils.data import DataLoader
import torch
import PIL

# %% ../nbs/01_dataloaders.ipynb 3
def hf_ds_collate_fn(data, flatten=True):
    '''
    Collation function for building a PyTorch DataLoader from a a huggingface dataset.
    Tries to put all items from an entry into the dataset to tensor.
    PIL images are converted to tensor, either flattened or not 
    '''

    def to_tensor(i, flatten):
        if isinstance(i, PIL.Image.Image):
            if flatten:
                return torch.flatten(TF.to_tensor(i))
            return TF.to_tensor(i)
        else:
            return torch.tensor(i)
    
    to_tensor = partial(to_tensor, flatten=flatten)      # partially apply to_tensor() with flatten arg
    data = (list(map(to_tensor, el.values())) for el in data)    # map each item from a dataset entry through to_tensor()
    data = zip(*data)                                    # zip data of any length not just (x,y) but also (x,y,z)
    return (torch.stack(i) for i in data)

# %% ../nbs/01_dataloaders.ipynb 4
class DataLoaders:
    def __init__(self, train, valid):
        '''Class that exposes two PyTorch dataloaders as train and valid arguments'''
        self.train = train
        self.valid = valid
    
    @classmethod
    def _get_dls(cls, train_ds, valid_ds, bs, collate_fn, **kwargs):
        '''Helper function returning 2 PyTorch Dataloaders as a tuple for 2 Datasets. **kwargs are passed to the DataLoader'''
        return (DataLoader(train_ds, batch_size=bs, shuffle=True, collate_fn=collate_fn, **kwargs),
                DataLoader(valid_ds, batch_size=bs*2, collate_fn=collate_fn, **kwargs))
        
    @classmethod
    def from_hf_dd(cls, dd, batch_size, collate_fn=hf_ds_collate_fn, **kwargs):
        '''Factory method to create a Dataloaders object for a Huggingface Dataset dict,
        uses the `hf_ds_collate_func` collation function by default, **kwargs are passes to the DataLoaders'''
        return cls(*cls._get_dls(*dd.values(), batch_size, collate_fn, **kwargs))
