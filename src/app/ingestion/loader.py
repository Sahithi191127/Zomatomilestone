"""
DatasetLoader — fetch Zomato data from Hugging Face.

HF dataset: ManikaSaini/zomato-restaurant-recommendation
Verified schema (datasets-server API):
  url, address, name, online_order, book_table, rate, votes, phone,
  location, rest_type, dish_liked, cuisines,
  approx_cost(for two people), reviews_list, menu_item,
  listed_in(type), listed_in(city)
"""

from __future__ import annotations

import pandas as pd
from datasets import load_dataset

from app.config import settings

DATASET_NAME = settings.hf_dataset_name


def load_raw_dataset() -> pd.DataFrame:
    """Load the Hugging Face dataset split as a pandas DataFrame."""
    ds = load_dataset(DATASET_NAME, split="train")
    return ds.to_pandas()
