# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_dataloaders.ipynb.

# %% auto 0
__all__ = ['hf_ds_collate_func', 'DataLoaders']

# %% ../nbs/01_dataloaders.ipynb 1
import torchvision.transforms.functional as TF
from torch.utils.data import DataLoader
import torch
import PIL

# %% ../nbs/01_dataloaders.ipynb 2
def hf_ds_collate_func(data):
    '''
    Collation function for building a PyTorch DataLoader from a a huggingface dataset.
    Tries to put all items from an entry into the dataset to tensor.
    PIL images are converted to tensor.
    '''

    def to_tensor(i):
        if isinstance(i, PIL.Image.Image):
            return TF.to_tensor(i).view(-1)
        else:
            return torch.tensor(i)
    
    data = [map(to_tensor, el.values()) for el in data]  # map each item from a dataset entry through to_tensor()
    data = zip(*data)                                    # zip data of any length not just (x,y) but also (x,y,z)
    return (torch.stack(i) for i in data)                

# %% ../nbs/01_dataloaders.ipynb 3
class DataLoaders:
    def __init__(self, train, valid):
        self.train = train
        self.valid = valid
    
    @classmethod
    def _get_dls(cls, train_ds, valid_ds, bs, collate_fn):
        return (DataLoader(train_ds, batch_size=bs, shuffle=True, collate_fn=collate_fn),
                DataLoader(valid_ds, batch_size=bs*2, collate_fn=collate_fn))
        
    @classmethod
    def from_hf_dd(cls, dd, batch_size):
        return cls(*cls._get_dls(*dd.values(), batch_size, hf_ds_collate_func))