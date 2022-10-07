class SLNode:
    """
    Singly Linked List Node class
    DO NOT CHANGE THIS CLASS IN ANY WAY
    """
    def __init__(self, value: object, next=None) -> None:
        self.value = value
        self.next = next

class QueueException(Exception):
    """
    Custom exception to be used by Queue class
    DO NOT CHANGE THIS METHOD IN ANY WAY
    """
    pass


class Queue:
    def __init__(self):
        """
        Initialize new queue with head and tail nodes
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        self._head = None
        self._tail = None

    def __str__(self):
        """
        Return content of queue in human-readable form
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        out = 'QUEUE ['
        if not self.is_empty():
            node = self._head
            out = out + str(node.value)
            node = node.next
            while node:
                out = out + ' -> ' + str(node.value)
                node = node.next
        return out + ']'

    def is_empty(self) -> bool:
        """
        Return True is the queue is empty, False otherwise
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        return self._head is None

    def size(self) -> int:
        """
        Return number of elements currently in the queue
        DO NOT CHANGE THIS METHOD IN ANY WAY
        """
        node = self._head
        length = 0
        while node:
            length += 1
            node = node.next
        return length

    # -----------------------------------------------------------------------

    def enqueue(self, value: object) -> None:
        """
        adds value to the end of the queue
        """
        new_node = SLNode(value)

        if self._head == None:  # head and tail point to same value if empty
            self._head = new_node
            self._tail = self._head
            return

        self._tail.next = new_node #only tail changes where it points
        self._tail = new_node

    def dequeue(self) -> object:
        """
        removes and returns value from front of the SLL queue
        """
        if self._head == None:
            raise QueueException

        new_node = self._head
        self._head = new_node.next #only head changes where it points
        return new_node.value

    def front(self) -> object:
        """
        returns value from front of the SLL queue
        """
        if self._head == None:
            raise QueueException

        new_node = self._head
        return new_node.value
