class ConsumptionTextReport:
    def __init__(self, p=None):
        self.y_unit_map = 'sum_btu'
        self.y_units = 'mmbtus'
        self.electric_unit_factor = 0
        self.gas_unit_factor = 0
        self.btu_unit_factor = 0

        self.electric_to_mmbtu_factor = 0
        self.gas_to_mmbtu_factor = 0
        self.btu_to_mmbtu_factor = 0

        self.entity_data = []

        self.grand_total_utility = 0
        self.grand_total_benchmark = 0
        self.grand_total_reported = 0
        self.grand_total_hours = 0
        self.grand_total_reported_hours = 0
        self.grand_total_benchmark_hours = 0
        self.grand_total_price_normalization = 0
        self.grand_total_cost_reduction = 0
        
        self.entity_electric_account_data = []
        self.entity_gas_account_data = []
        self.entity_all_account_data = []
    
        self.entity_electric_utility = 0
        self.entity_electric_reported = 0
        self.entity_electric_benchmark = 0
        self.entity_electric_hours = 0
        self.entity_electric_reported_hours = 0
        self.entity_electric_benchmark_hours = 0
        self.entity_electric_price_normalization = 0
        self.entity_electric_cost_reduction = 0
        self.entity_gas_utility = 0
        self.entity_gas_reported = 0
        self.entity_gas_benchmark = 0
        self.entity_gas_hours = 0
        self.entity_gas_reported_hours = 0
        self.entity_gas_benchmark_hours = 0
        self.entity_gas_price_normalization = 0
        self.entity_gas_cost_reduction = 0

        self.account_utility = 0
        self.account_reported = 0
        self.account_benchmark = 0
        self.account_hours = 0
        self.account_reported_hours = 0
        self.account_price_normalization = 0
        self.account_benchmark_hours = 0
        self.account_cost_reduction = 0
        self.account_difference = 0
        self.account_change = 0 
        
        self.entity_all_utility = 0
        self.entity_all_reported = 0
        self.entity_all_benchmark = 0
        self.entity_all_price_normalization = 0
        self.entity_all_hours = 0
        self.entity_all_benchmark_hours = 0
        self.entity_all_reported_hours = 0
        self.entity_all_cost_reduction = 0
        self.entity_all_difference = 0
        self.entity_all_change = 0
        
        self.account_utility_btu = 0
        self.account_reported_btu = 0
        self.account_benchmark_btu = 0
        self.account_difference_btu = 0
        self.account_change_btu = 0

        if p:
            self.__dict__.update(**p)