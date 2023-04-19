class FclFreightVyuh():
    def __init__(self, rates: list = []):
        self.rates = rates
    
    def check_fulfilment_ratio(self):
        return 100

    def apply_dynamic_price(self):
        print(self.rates)
        return self.rates