class Invocation():
    def __init__(self, ctx, logger):
        self.logger = logger
        self.ctx = ctx
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
        self.logger(f'Early time set to {self.remtimeEarly} and reminder time set to {self.remtime}')
