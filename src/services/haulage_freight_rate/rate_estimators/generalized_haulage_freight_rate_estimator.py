
from fastapi import HTTPException


class GeneralizedHaulageFreightRateEstimator:
    def __init__(self, *_, **__):
        pass

    def estimate(self):
        """
        Primary Function to estimate generalized prices
        """
        raise HTTPException(status_code=400, detail="rates not present")
