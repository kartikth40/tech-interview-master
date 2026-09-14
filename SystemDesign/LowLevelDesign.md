# Low-Level Design (LLD) Interview Guide

## What is LLD?

Low-Level Design focuses on the **code-level architecture** of a system - class diagrams, design patterns, interfaces, and object relationships. LLD interviews are common at the entry-to-mid level and test your ability to translate requirements into clean, extensible code.

> 🧭 Prefer the *visual* thinking layer - the modeling process as a flowchart, a "which pattern?"
> decision tree, a SOLID-fix map, and a UML class-diagram example? See
> **[LLD Mental Models](lld-mental-models.md)**.

**LLD vs HLD:**
| | High-Level Design | Low-Level Design |
|--|--|--|
| Focus | System components, data flow | Classes, interfaces, patterns |
| Output | Architecture diagram | Class diagram + code |
| Scale | Distributed systems | Single service/module |
| Time | 30-45 min | 30-45 min |

---

## LLD Interview Framework (Use Every Time)

### Step 1: Clarify Requirements (5 min)
- What are the core entities?
- What operations are needed?
- Any constraints (thread safety, extensibility)?

### Step 2: Identify Entities & Relationships (5 min)
- Nouns → Classes
- Verbs → Methods
- Relationships → Associations, Inheritance, Composition

### Step 3: Define Interfaces & Abstractions (5 min)
- What should be abstract vs concrete?
- Where do you need extensibility?

### Step 4: Apply Design Patterns (10 min)
- Which patterns fit naturally?
- Don't force patterns - use them when they solve a real problem

### Step 5: Write Core Code (15 min)
- Implement key classes
- Show method signatures and logic
- Handle edge cases

### Step 6: Discuss Trade-offs (5 min)
- Thread safety
- Extensibility
- Performance

---

## SOLID Principles

Every LLD answer should demonstrate SOLID awareness.

### S - Single Responsibility Principle
> A class should have only one reason to change.

```python
# ❌ Bad: One class doing too much
class UserManager:
    def create_user(self, data): ...
    def send_welcome_email(self, user): ...  # Email logic here?
    def save_to_database(self, user): ...     # DB logic here?


# ✅ Good: Separate responsibilities
class UserService:
    def __init__(self, user_repo, email_service):
        self.user_repo = user_repo
        self.email_service = email_service

    def create_user(self, data):
        user = User(data)
        self.user_repo.save(user)
        self.email_service.send_welcome(user)
        return user


class UserRepository:
    def save(self, user): ...      # DB logic
    def find_by_id(self, id): ...  # DB logic


class EmailService:
    def send_welcome(self, user): ...  # Email logic
```

---

### O - Open/Closed Principle
> Open for extension, closed for modification.

```python
from abc import ABC, abstractmethod


# ❌ Bad: Adding a new payment type requires modifying the existing class
class PaymentProcessor:
    def process(self, type, amount):
        if type == "credit":
            ...
        elif type == "debit":
            ...
        elif type == "upi":
            ...  # keep adding branches?


# ✅ Good: Extend without modifying
class Payment(ABC):
    @abstractmethod
    def execute(self): ...


class PaymentProcessor:
    def process(self, payment: Payment):
        payment.execute()  # polymorphism


class CreditCardPayment(Payment):
    def execute(self): ...  # credit card logic


class UPIPayment(Payment):
    def execute(self): ...  # UPI logic


class CryptoPayment(Payment):  # new type - no existing code changed
    def execute(self): ...  # crypto logic
```

---

### L - Liskov Substitution Principle
> Subtypes must be substitutable for their base types.

```python
from abc import ABC, abstractmethod


# ❌ Bad: Square breaks Rectangle's contract
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h
    def area(self): return self.width * self.height


class Square(Rectangle):
    def set_width(self, w): self.width = self.height = w   # breaks LSP!
    def set_height(self, h): self.width = self.height = h  # breaks LSP!


# ✅ Good: Use a separate hierarchy
class Shape(ABC):
    @abstractmethod
    def area(self): ...


class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h

    def area(self):
        return self.w * self.h


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side * self.side
```

---

### I - Interface Segregation Principle
> Clients should not be forced to depend on interfaces they don't use.

```python
from abc import ABC, abstractmethod


# ❌ Bad: Fat interface forces all implementors to implement everything
class Animal(ABC):
    @abstractmethod
    def eat(self): ...
    @abstractmethod
    def sleep(self): ...
    @abstractmethod
    def fly(self): ...   # not all animals fly!
    @abstractmethod
    def swim(self): ...  # not all animals swim!


# ✅ Good: Segregated interfaces (mixins)
class Animal(ABC):
    @abstractmethod
    def eat(self): ...
    @abstractmethod
    def sleep(self): ...


class Flyable(ABC):
    @abstractmethod
    def fly(self): ...


class Swimmable(ABC):
    @abstractmethod
    def swim(self): ...


# Duck can fly AND swim
class Duck(Animal, Flyable, Swimmable):
    def eat(self): ...
    def sleep(self): ...
    def fly(self): ...
    def swim(self): ...


# Dog can only swim
class Dog(Animal, Swimmable):
    def eat(self): ...
    def sleep(self): ...
    def swim(self): ...
```

---

### D - Dependency Inversion Principle
> Depend on abstractions, not concretions.

```python
# ❌ Bad: High-level module depends on a low-level module
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()  # tightly coupled to MySQL!


# ✅ Good: Depend on an abstraction (inject the dependency)
class OrderService:
    def __init__(self, database):
        self.db = database

    def create_order(self, data):
        return self.db.save(data)


# Swap implementations without changing OrderService
mysql_service = OrderService(MySQLDatabase())
mongo_service = OrderService(MongoDatabase())
test_service = OrderService(InMemoryDatabase())
```

---

## Design Patterns (Interview Essentials)

### Creational Patterns

#### Singleton
> Ensure only one instance of a class exists.

```python
class DatabaseConnection:
    _instance = None

    def __new__(cls, config=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = cls._connect(config)
        return cls._instance

    @classmethod
    def get_instance(cls, config=None):
        if cls._instance is None:
            cls(config)
        return cls._instance

    @staticmethod
    def _connect(config):
        # establish connection
        return {"host": config["host"], "status": "connected"}


# Usage
db1 = DatabaseConnection.get_instance({"host": "localhost"})
db2 = DatabaseConnection.get_instance()
print(db1 is db2)  # True
```

**Use when:** Logger, config manager, connection pool, cache

---

#### Factory Method
> Let a factory decide which class to instantiate.

```python
class EmailNotification:
    def send(self, to, message):
        print(f"Email to {to}: {message}")


class SMSNotification:
    def send(self, to, message):
        print(f"SMS to {to}: {message}")


class PushNotification:
    def send(self, to, message):
        print(f"Push to {to}: {message}")


class NotificationFactory:
    @staticmethod
    def create(type):
        factories = {
            "email": EmailNotification,
            "sms": SMSNotification,
            "push": PushNotification,
        }
        if type not in factories:
            raise ValueError(f"Unknown notification type: {type}")
        return factories[type]()


# Usage
notif = NotificationFactory.create("email")
notif.send("user@example.com", "Welcome!")
```

**Use when:** Object creation logic is complex or varies by type

---

#### Builder
> Construct complex objects step by step.

Each setter returns `self` so calls chain fluently, and a final `build()` produces the object:
```python
sql = (QueryBuilder().from_("users").select("id", "name")
       .where("age > 18").limit_to(10).build())
# each method sets a field on an internal dict and `return self`; build() assembles the result
```

**Use when:** Object has many optional parameters (avoids telescoping constructors)

---

### Structural Patterns

#### Adapter
> Convert one interface to another that clients expect.

Wrap the incompatible object and expose the interface your app wants; the adapter translates
calls/return shapes internally:
```python
class PaymentAdapter:            # app calls pay(...); legacy exposes make_payment(...)
    def __init__(self, legacy): self.legacy = legacy
    def pay(self, card, amount, currency):
        r = self.legacy.make_payment(card, amount, currency)
        return {"success": r["status"] == "success", "id": r["transaction_id"]}
```

**Use when:** Integrating third-party libraries, legacy code migration

---

#### Decorator
> Add behavior to objects dynamically without subclassing.

Each decorator wraps a component sharing the same interface and augments its result, so you stack
them at runtime:
```python
class MilkDecorator:                       # same interface as Coffee
    def __init__(self, coffee): self.coffee = coffee
    def cost(self): return self.coffee.cost() + 15
    def description(self): return self.coffee.description() + ", milk"

coffee = MilkDecorator(SugarDecorator(Coffee()))   # wrap to add features
```

**Use when:** Adding features to objects at runtime (logging, auth, caching middleware)

---

#### Proxy
> Control access to an object (same interface as the real object, adds a gate).

```python
class CachingProxy:                        # same interface as the real service
    def __init__(self, service): self.service, self.cache = service, {}
    def fetch_data(self, key):
        if key not in self.cache:          # add caching / auth / lazy-init here
            self.cache[key] = self.service.fetch_data(key)
        return self.cache[key]
```

**Use when:** Lazy loading, caching, access control, logging

---

### Behavioral Patterns

#### Observer
> Define a one-to-many dependency so when one object changes, all dependents are notified.

```python
from collections import defaultdict


class EventEmitter:
    def __init__(self):
        self.listeners = defaultdict(list)

    def on(self, event, callback):
        self.listeners[event].append(callback)
        return self

    def off(self, event, callback):
        self.listeners[event] = [cb for cb in self.listeners[event] if cb != callback]

    def emit(self, event, data):
        for cb in self.listeners[event]:
            cb(data)


# Usage: Order system
order_events = EventEmitter()

order_events.on("order:placed", lambda d: print(f"Send confirmation email for order {d['order_id']}"))
order_events.on("order:placed", lambda d: print(f"Notify warehouse for order {d['order_id']}"))
order_events.on("order:placed", lambda d: print(f"Update analytics for order {d['order_id']}"))

order_events.emit("order:placed", {"order_id": "ORD-001"})
# All 3 handlers fire
```

**Use when:** Event systems, pub/sub, UI state management, notifications

---

#### Strategy
> Define a family of algorithms, encapsulate each one, make them interchangeable.

```python
from abc import ABC, abstractmethod


class SortStrategy(ABC):
    @abstractmethod
    def sort(self, arr): ...


class BubbleSort(SortStrategy):
    def sort(self, arr):
        a = list(arr)
        for i in range(len(a)):
            for j in range(len(a) - i - 1):
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
        return a


class QuickSort(SortStrategy):
    def sort(self, arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[-1]
        left = [x for x in arr[:-1] if x <= pivot]
        right = [x for x in arr[:-1] if x > pivot]
        return self.sort(left) + [pivot] + self.sort(right)


class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort(self, arr):
        return self.strategy.sort(arr)


# Usage
sorter = Sorter(QuickSort())
sorter.sort([3, 1, 4, 1, 5])

# Swap strategy at runtime
sorter.set_strategy(BubbleSort())
sorter.sort([3, 1, 4, 1, 5])
```

**Use when:** Multiple algorithms for same task, runtime algorithm selection

---

#### Command
> Encapsulate a request as an object with `execute()` + `undo()`, enabling undo/redo.

Each command knows how to do and reverse itself; an invoker keeps a history stack:
```python
class InsertCommand:                       # each command stores what it needs to undo
    def __init__(self, text): self.text = text
    def execute(self, editor): editor.text += self.text
    def undo(self, editor):    editor.text = editor.text[:-len(self.text)]

# Invoker: execute(cmd) runs it and pushes to history; undo() pops and calls cmd.undo()
```

**Use when:** Undo/redo, transaction queues, macro recording

---

## Common LLD Interview Problems

### 1. Parking Lot

```python
# Entities: ParkingLot, ParkingFloor, ParkingSpot, Vehicle, ParkingTicket
import time


class Vehicle:
    def __init__(self, plate, type):
        self.plate = plate
        self.type = type  # 'bike', 'car', 'truck'


class ParkingSpot:
    def __init__(self, id, type):
        self.id = id
        self.type = type  # 'small', 'medium', 'large'
        self.vehicle = None

    def is_available(self):
        return self.vehicle is None

    def can_fit(self, vehicle):
        fits = {
            "small": ["bike"],
            "medium": ["bike", "car"],
            "large": ["bike", "car", "truck"],
        }
        return vehicle.type in fits[self.type]

    def park(self, vehicle):
        self.vehicle = vehicle

    def vacate(self):
        self.vehicle = None


class ParkingFloor:
    def __init__(self, floor_num, spots):
        self.floor_num = floor_num
        self.spots = spots

    def find_available_spot(self, vehicle):
        for s in self.spots:
            if s.is_available() and s.can_fit(vehicle):
                return s
        return None


class ParkingTicket:
    def __init__(self, vehicle, spot, floor):
        self.id = f"TKT-{int(time.time() * 1000)}"
        self.vehicle = vehicle
        self.spot = spot
        self.floor = floor
        self.entry_time = time.time()
        self.exit_time = None

    def checkout(self):
        self.exit_time = time.time()
        self.spot.vacate()
        return self._calculate_fee()

    def _calculate_fee(self):
        import math
        hours = math.ceil((self.exit_time - self.entry_time) / 3600)
        rates = {"small": 20, "medium": 40, "large": 60}
        return hours * rates[self.spot.type]


class ParkingLot:
    def __init__(self, floors):
        self.floors = floors
        self.active_tickets = {}

    def park(self, vehicle):
        for floor in self.floors:
            spot = floor.find_available_spot(vehicle)
            if spot:
                spot.park(vehicle)
                ticket = ParkingTicket(vehicle, spot, floor)
                self.active_tickets[ticket.id] = ticket
                return ticket
        raise RuntimeError("Parking lot is full")

    def checkout(self, ticket_id):
        ticket = self.active_tickets.get(ticket_id)
        if not ticket:
            raise ValueError("Invalid ticket")
        fee = ticket.checkout()
        del self.active_tickets[ticket_id]
        return fee
```

---

### 2. Elevator System

```python
# Entities: ElevatorSystem, Elevator, Request, Direction


class Request:
    def __init__(self, floor, direction):
        self.floor = floor
        self.direction = direction  # 'up' | 'down'


class Elevator:
    def __init__(self, id, total_floors):
        self.id = id
        self.current_floor = 0
        self.direction = "idle"  # 'up' | 'down' | 'idle'
        self.destinations = set()
        self.total_floors = total_floors

    def add_destination(self, floor):
        self.destinations.add(floor)
        self._update_direction()

    def move(self):
        if not self.destinations:
            self.direction = "idle"
            return

        if self.direction == "up":
            self.current_floor += 1
        elif self.direction == "down":
            self.current_floor -= 1

        if self.current_floor in self.destinations:
            self.destinations.discard(self.current_floor)
            print(f"Elevator {self.id} stopped at floor {self.current_floor}")

        self._update_direction()

    def _update_direction(self):
        if not self.destinations:
            self.direction = "idle"
            return
        max_dest = max(self.destinations)
        min_dest = min(self.destinations)
        if self.direction == "up" and max_dest > self.current_floor:
            return
        if self.direction == "down" and min_dest < self.current_floor:
            return
        self.direction = "up" if max_dest > self.current_floor else "down"

    def distance_to(self, floor):
        return abs(self.current_floor - floor)


class ElevatorSystem:
    def __init__(self, num_elevators, total_floors):
        self.elevators = [Elevator(i, total_floors) for i in range(num_elevators)]

    # Dispatch: find nearest idle or same-direction elevator
    def dispatch(self, request):
        candidates = [
            e for e in self.elevators
            if e.direction == "idle" or e.direction == request.direction
        ]
        pool = candidates or self.elevators
        best = min(pool, key=lambda e: e.distance_to(request.floor))
        best.add_destination(request.floor)
        return best
```

---

### 3. Rate Limiter

```python
# Token Bucket Algorithm
import time


class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity        # max tokens
        self.tokens = capacity          # current tokens
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self, tokens=1):
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True   # allowed
        return False      # rate limited


class RateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = {}  # user_id -> TokenBucket

    def is_allowed(self, user_id):
        if user_id not in self.buckets:
            self.buckets[user_id] = TokenBucket(self.capacity, self.refill_rate)
        return self.buckets[user_id].consume()


# Usage: 10 requests/sec per user
limiter = RateLimiter(10, 10)
print(limiter.is_allowed("user1"))  # True
```

---

## Design Pattern Quick Reference

| Pattern | Category | Use When |
|---------|----------|----------|
| Singleton | Creational | One instance needed (DB, Logger) |
| Factory | Creational | Object creation varies by type |
| Builder | Creational | Complex object with many options |
| Adapter | Structural | Incompatible interfaces |
| Decorator | Structural | Add behavior dynamically |
| Proxy | Structural | Control access (cache, auth) |
| Observer | Behavioral | One-to-many event notification |
| Strategy | Behavioral | Interchangeable algorithms |
| Command | Behavioral | Undo/redo, queued operations |

---

## Common LLD Mistakes

| Mistake | Fix |
|---------|-----|
| God class (one class does everything) | Apply SRP, split responsibilities |
| Hardcoded dependencies | Use dependency injection |
| No interfaces/abstractions | Program to interfaces (abc.ABC), not implementations |
| Inheritance over composition | Prefer composition for flexibility |
| Ignoring thread safety | Mention locks/atomic ops for shared state |
| Over-engineering | Start simple, add patterns only when needed |

---

## Interview Tips

1. **Start with entities** - list all nouns from the problem
2. **Draw the class diagram first** - relationships before code
3. **Apply patterns naturally** - don't force them
4. **Mention extensibility** - "If we add X later, we'd just..."
5. **Talk about thread safety** - especially for Singleton, shared state
6. **Keep it simple** - interviewers want clean code, not clever code

---

## Related Resources

- [System Design Guide](SystemDesignGuide.md)
- [API Design Patterns](APIDesignPatterns.md)
