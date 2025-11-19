class UIStateManager:
    def __init__(self):
        self.screens = {}
        self.active = None
    def add(self, name, screen):
        self.screens[name] = screen
    def set(self, name):
        self.active = self.screens[name]
    def handle_event(self, e):
        if self.active: self.active.handle_event(e)
    def update(self, dt):
        if self.active: self.active.update(dt)
    def draw(self, surf):
        if self.active: self.active.draw(surf)