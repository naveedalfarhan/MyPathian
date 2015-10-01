class Committee:

    def __init__(self, p=None):
        self.id = None
        self.name = None
        self.group_id = None
        self.corporate_energy_director_id = None
        self.facility_directors_ids = []
        self.team_members_ids = []

        if p:
            if "id" in p:
                self.id = p['id']
            if "name" in p:
                self.name = p['name']
            if "group_id" in p:
                self.group_id = p['group_id']
            if "corporate_energy_director_id" in p:
                self.corporate_energy_director_id = p['corporate_energy_director_id']
            if "facility_directors_ids" in p:
                self.facility_directors_ids = p['facility_directors_ids']
            if "team_members_ids" in p:
                self.team_members_ids = p['team_members_ids']