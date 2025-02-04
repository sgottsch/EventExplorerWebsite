class Aspect:

    def __init__(self, aspect_id, name, description=None):
        self.id = aspect_id
        self.name = name[0].upper() + name[1:]

        # self.name = str(name)[0].upper() + str(name)[1:]
        if self.name in ["When", "Who", "Where", "Why", "What", "How"]:
            self.name = self.name + "?"
        self.description = description
        self.sub_aspects = []
        self.is_last = False

    def sort_sub_aspects(self):
        if self.sub_aspects:
            aspect_dict = {}
            for sub_aspect in self.sub_aspects:
                aspect_dict[sub_aspect.name] = sub_aspect
            sorted_sub_aspects = sorted([aspect.name for aspect in self.sub_aspects])
            self.sub_aspects = []
            for sub_aspect_name in sorted_sub_aspects:
                self.sub_aspects.append(aspect_dict[sub_aspect_name])
