from fastapi import HTTPException
class HaulageFreightRateWeightSlab:
    def __init__(self):
        self.lower_limit = None
        self.upper_limit = None
        self.price = None
        self.currency = None
        self.remarks = []

    def validate(self):
        if self.lower_limit is None or self.upper_limit is None:
            raise HTTPException(status_code=400,detail="Lower limit and upper limit must be present")
        if self.price is not None and self.price < 0:
            raise HTTPException(status_code=400,detail="Price must be greater than or equal to 0")

