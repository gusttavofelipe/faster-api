import sys

# SEM __slots__
class TransactionNoSlots:
    def __init__(self, session):
        self.session = session
        self._in_transaction = False

# COM __slots__
class TransactionWithSlots:
    __slots__ = ("session", "_in_transaction")
    
    def __init__(self, session):
        self.session = session
        self._in_transaction = False


session = object()


no_slots = TransactionNoSlots(session)
with_slots = TransactionWithSlots(session)

# objeto + __dict__ (se existir)
size_no_slots = sys.getsizeof(no_slots) + sys.getsizeof(no_slots.__dict__)
size_with_slots = sys.getsizeof(with_slots)

print(f"Sem __slots__: {size_no_slots} bytes")
print(f"Com __slots__: {size_with_slots} bytes")
print(f"diferença: {size_no_slots - size_with_slots} bytes ({((size_no_slots - size_with_slots) / size_no_slots * 100):.1f}%)")


with_slots.__dict__