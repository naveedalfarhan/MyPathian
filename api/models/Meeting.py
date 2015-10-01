class Meeting:
    def __init__(self, p=None):
        self.id = None
        self.title = None
        self.date = None
        self.location = None
        self.description = None
        self.group_id = None
        self.meeting_type_id = None
        self.project_id = None
        self.called_by_id = None
        self.note_taker_id = None
        self.facilitator_id = None
        self.time_keeper_id = None
        self.attendees_ids = None
        self.notes = None

        if p:
            if "id" in p:
                self.id = p['id']
            if "title" in p:
                self.title = p['title']
            if "date" in p:
                self.date = p['date']
            if "location" in p:
                self.location = p['location']
            if "description" in p:
                self.description = p['description']
            if "group_id" in p:
                self.group_id = p['group_id']
            if "meeting_type_id" in p:
                self.meeting_type_id = p['meeting_type_id']
            if "project_id" in p:
                self.project_id = p['project_id']
            if "called_by_id" in p:
                self.called_by_id = p['called_by_id']
            if "note_taker_id" in p:
                self.note_taker_id = p['note_taker_id']
            if "facilitator_id" in p:
                self.facilitator_id = p['facilitator_id']
            if "time_keeper_id" in p:
                self.time_keeper_id = p['time_keeper_id']
            if "attendees_ids" in p:
                self.attendees_ids = p['attendees_ids']
            if "notes" in p:
                self.notes = p['notes']