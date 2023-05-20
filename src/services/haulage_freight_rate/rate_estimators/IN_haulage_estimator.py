class INHaulageRateEstimator():
    def __init__(self, origin_location_id, destination_location_id):
        self.origin_location_id = origin_location_id,
        self.destination_location_id = destination_location_id
    
    def convert_general_params_to_estimation_params(self):
        return True
    
    def get_final_estimated_price(self, estimator_params):
        return 10
    

    def estimate(self):
        ''' 
        Primary Function to estimate india prices
        '''
        print('Estimating India rates')
        estimator_params = self.convert_general_params_to_estimation_params()
        final_price = self.get_final_estimated_price(estimator_params=estimator_params)
        return final_price
        