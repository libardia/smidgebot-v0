import logger

class Invocation():
    def __init__(self, ctx, logger):
        self.exclude = []
        self.earlyCond = False
        self.mainCond = False
        self.remtime = None
        self.remtimeEarly = None
        # By default, 7pm CST on Saturday
        self.setRemtime((5, 19, 0))
    
    def setRemtime(self, remtime):
        self.remtime = remtime
        d, h, m = remtime
        m -= 30
        if m < 0:
            h -= 1
            m += 60
        self.remtimeEarly = (d, h, m)
        logger.log(f'Early time set to {self.remtimeEarly} and reminder time set to {self.remtime}')

    def asstr(self)
        attributes = dir(self)
        res = self.__class__.__name__ + "("
        first = True
        for attr in attributes:
            if attr.startswith("__") and attr.endswith("__"):
                continue

            if(first):
                first = False
            else:
                res += ", "

            res += attr + " = " + str(getattr(self, attr))

        res += ")"
        return res

    def __repr__(self):
        return self.asstr()
