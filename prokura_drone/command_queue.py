import queue as Queue

class CommandQueue(Queue.Queue):
    
    def _init(self, maxsize):
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()

    def __contains__(self, item):
        with self.mutex:
            return item in self.queue

    @property
    def _size(self):
        return len(self.queue)