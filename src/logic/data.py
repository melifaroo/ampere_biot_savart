from collections import defaultdict

class DataManager:
    def __init__(self):
        self.data = defaultdict(list)

    def add_excitation_data(self, I, excitation_type, Kd):
        self.data['I'].append(I)
        self.data['excitation_type'].append(excitation_type)
        self.data['Kd'].append(Kd)

    def get_excitation_data(self):
        return {
            'I': self.data['I'],
            'excitation_type': self.data['excitation_type'],
            'Kd': self.data['Kd']
        }

    def clear_data(self):
        self.data.clear()