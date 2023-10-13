'''
    Module contains Dataset class, collate function for DataLoader and loader getter function.

    * MiniFlickrDataset loads data from pickle file and returns image embedding and caption.
    * cl_fn is used to process batch of data and return tensors.
    * get_loader returns DataLoader object.
'''

import os
import pickle

import numpy as np

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import GPT2Tokenizer

class MiniFlickrDataset(Dataset):
    def __init__(self, path): 
        # check if file is file
        if not os.path.isfile(path):
            raise OSError('Dataset file not found. Downloading...')

        with open(path, 'rb') as f:
            self.data = pickle.load(f)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

# collate_fn for DataLoader
def cl_fn(batch, tokenizer):
    batch = list(zip(*batch))

    _, img_emb, cap = batch
    del batch

    img_emb = torch.tensor(np.array(img_emb)) # better to convert list to numpy array first, then to tensor
    cap = tokenizer(cap, padding=True, return_tensors='pt')

    input_ids, attention_mask = cap['input_ids'], cap['attention_mask']

    return img_emb, input_ids, attention_mask

def get_loader(dataset, bs_exp=5, shuffle=True, num_workers=0, pin_memory=False):
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2-medium')
    tokenizer.pad_token = tokenizer.eos_token

    return DataLoader(
        dataset, 
        batch_size=2**bs_exp, 
        collate_fn=lambda b: cl_fn(b, tokenizer),
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory
    )