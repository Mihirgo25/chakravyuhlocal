
from typing import Callable, List

def get_in_batches(method: Callable[[List, int], List], to_batch_params: List = [], BATCH_SIZE: int = 500):
    '''
    Arguments
     - method: function to invoke for getting results
     - to_batch_params: function parameter to batch
     - BATCH_SIZE: Size of each batch
    
    returns
     - Combined result of batches in a single list
    '''

    total_data = len(to_batch_params)
    final_results = []

    batch_start = 0
    
    while total_data > batch_start:
        batch_end = batch_start + BATCH_SIZE
        batched_ids = to_batch_params[batch_start:batch_end]
        batch_results = method(batched_ids, BATCH_SIZE)
        batch_results = batch_results or []
        final_results = final_results + batch_results
        batch_start = batch_end

    return final_results
