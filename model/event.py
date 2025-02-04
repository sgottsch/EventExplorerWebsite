class Event:

    def __init__(self, id, name):
        self.id = id
        self.name = name

        self.name_nice = name.replace("_", " ")
        self.name_nice = self.name_nice[0].upper() + self.name_nice[1:]

        self.aspects = []
        self.aspects_dict = dict()
        self.rankings = dict()
        self.global_ranking = None
