import logger

class Invocation():
    def __init__(self):
        self.exclude = []
        self.earlyCond = False
        self.mainCond = False
        self.remtime = None
        self.remtimeEarly = None
    
    async def setRemtime(self, remtime):
        self.remtime = remtime
        d, h, m = remtime
        m -= 30
        if m < 0:
            h -= 1
            m += 60
        self.remtimeEarly = (d, h, m)
        await logger.log(f'Early time set to {self.remtimeEarly} and reminder time set to {self.remtime}')
