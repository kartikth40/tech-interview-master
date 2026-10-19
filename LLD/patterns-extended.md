---
title: Design Patterns - Extended
description: Mid-level design patterns beyond the common eight - Command, Chain of Responsibility, Template Method, Facade, Proxy, Composite, Null Object - with trade-offs, "when NOT to use" guidance, and a pattern-selection cheat sheet.
---

# Design Patterns - Extended

The [Roadmap](roadmap.md#6-design-patterns) covers the common eight (Singleton, Factory, Builder,
Adapter, Decorator, Strategy, Observer, State). This page adds the patterns that show up at
mid-level and - more importantly - the **trade-offs and "when NOT to use"** judgement
interviewers probe. For compact runnable examples of the common patterns, see the
[Low-Level Design Guide](LowLevelDesign.md).

!!! note "Language"
    Python primary; Java where the idiom matters ([Java Cheat Sheet](java-cheatsheet.md)).

## The meta-skill: justify, don't name-drop

At SDE-2 the pattern itself is table stakes. What distinguishes you:

- **Recognize the need** before naming the pattern ("these are interchangeable algorithms →
  Strategy", not "let me apply Strategy").
- **State the trade-off**: every pattern adds indirection = more classes = harder to read.
  Patterns pay for flexibility you actually need; don't pre-pay.
- **Know the alternative**: Strategy vs a simple `if/else`; Builder vs a dataclass with
  defaults; Observer vs a direct call. Picking the simpler one *with reasoning* scores higher
  than forcing a pattern.

> Red flag: "I'll use the Factory pattern" with no reason. Green flag: "Creation varies by
> input and I want callers decoupled from concrete classes, so a Factory earns its place."

---

## Command - encapsulate a request as an object

**Use for:** undo/redo, queuing requests, logging/replaying operations, macro commands.
Each action becomes an object with `execute()` (and often `undo()`).

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class AddTextCommand(Command):
    def __init__(self, doc, text):
        self.doc, self.text = doc, text
    def execute(self): self.doc.append(self.text)
    def undo(self):    self.doc.pop()

class Editor:                         # invoker - keeps history, doesn't know command internals
    def __init__(self): self.history = []
    def run(self, cmd: Command):
        cmd.execute()
        self.history.append(cmd)
    def undo(self):
        if self.history:
            self.history.pop().undo()
```

- Decouples the **invoker** (who triggers) from the **receiver** (who does the work).
- **Don't use** if there's no undo/queue/log need - it's just an extra indirection otherwise.

---

## Chain of Responsibility - pass a request along a chain

**Use for:** middleware pipelines, approval chains, validation chains, event filters,
logging levels. Each handler either handles the request or passes it on.

```python
from abc import ABC, abstractmethod

class Handler(ABC):
    def __init__(self):
        self._next = None
    def set_next(self, h):
        self._next = h
        return h                       # enables fluent chaining
    @abstractmethod
    def handle(self, request): ...

class AuthHandler(Handler):
    def handle(self, req):
        if not req.get("token"):
            return "401 Unauthorized"
        return self._next.handle(req) if self._next else "OK"

class RateLimitHandler(Handler):
    def handle(self, req):
        if req.get("count", 0) > 100:
            return "429 Too Many Requests"
        return self._next.handle(req) if self._next else "OK"

# wire the chain
auth = AuthHandler()
auth.set_next(RateLimitHandler())
print(auth.handle({"token": "x", "count": 5}))   # OK
```

- Each handler has one responsibility (SRP); add/remove/reorder handlers freely (OCP).
- **Don't use** for a fixed 2-step check - a chain is overkill.

Real LLD uses: expense approval (manager → director → VP by amount), request middleware,
money-dispensing in an ATM (dispense ₹2000 notes → ₹500 → ₹100).

---

## Template Method - fix the skeleton, vary the steps

**Use for:** algorithms with a fixed sequence but variable steps (data parsers, report
generators, game turns). Base class defines the order; subclasses fill in steps.

```python
from abc import ABC, abstractmethod

class DataExporter(ABC):
    def export(self, data):            # template method - fixed skeleton, DON'T override
        self.open()
        self.write_header()
        self.write_rows(data)          # varies
        self.close()
    def open(self):  print("open file")
    def close(self): print("close file")
    @abstractmethod
    def write_header(self): ...
    @abstractmethod
    def write_rows(self, data): ...

class CsvExporter(DataExporter):
    def write_header(self):      print("id,name")
    def write_rows(self, data):  print("\n".join(data))
```

- Strategy vs Template Method: Strategy varies an algorithm via **composition** (inject an
  object); Template Method varies steps via **inheritance** (override methods). Prefer
  Strategy when you want runtime swapping; Template Method when the skeleton is truly fixed.

---

## Facade - one simple front for a complex subsystem

**Use for:** hiding a messy set of subsystems behind one clean entry point (e.g. an
`OrderFacade` that coordinates inventory + payment + shipping + notification).

```python
class OrderFacade:
    def __init__(self, inventory, payment, shipping, notifier):
        self._inv, self._pay = inventory, payment
        self._ship, self._notify = shipping, notifier
    def place_order(self, user, item):          # client calls ONE method
        self._inv.reserve(item)
        self._pay.charge(user, item.price)
        self._ship.schedule(user, item)
        self._notify.send(user, "order placed")
```

- Simplifies the client's view; doesn't *restrict* access to subsystems (unlike encapsulation).
- **Don't confuse with Adapter**: Adapter changes an interface to match an expectation; Facade
  simplifies *many* interfaces into one.

---

## Proxy - stand-in that controls access

**Use for:** lazy loading (virtual proxy), access control (protection proxy), caching,
logging, remote calls. Same interface as the real object; adds a layer around it.

```python
from abc import ABC, abstractmethod

class Image(ABC):
    @abstractmethod
    def display(self): ...

class RealImage(Image):               # expensive to create
    def __init__(self, path):
        self.path = path
        self._load()                  # heavy disk load
    def _load(self): print(f"loading {self.path}")
    def display(self): print(f"showing {self.path}")

class ImageProxy(Image):              # defers creation until actually needed
    def __init__(self, path):
        self.path, self._real = path, None
    def display(self):
        if self._real is None:        # lazy load on first use
            self._real = RealImage(self.path)
        self._real.display()
```

- Proxy vs Decorator: both wrap and share the interface. **Decorator adds behavior**; **Proxy
  controls access** (may not even create the real object).

---

## Composite - treat individual objects and groups uniformly

**Use for:** tree structures where a leaf and a container should be used the same way - file
systems, UI components, org charts, menu + submenus.

```python
from abc import ABC, abstractmethod

class FileSystemNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

class File(FileSystemNode):           # leaf
    def __init__(self, size): self._size = size
    def size(self): return self._size

class Directory(FileSystemNode):      # composite
    def __init__(self): self.children = []
    def add(self, node): self.children.append(node)
    def size(self): return sum(c.size() for c in self.children)  # recurse uniformly

root = Directory()
root.add(File(100))
sub = Directory(); sub.add(File(50)); root.add(sub)
print(root.size())                    # 150 - same size() call on file or dir
```

---

## Null Object - a do-nothing default instead of `None`/`null`

**Use for:** avoiding null checks everywhere. Provide a neutral implementation.

```python
class Logger(ABC):
    @abstractmethod
    def log(self, msg): ...
class ConsoleLogger(Logger):
    def log(self, msg): print(msg)
class NullLogger(Logger):             # does nothing - no caller null-checks needed
    def log(self, msg): pass

def service(logger: Logger = NullLogger()):
    logger.log("started")             # safe even when "no logger" was wanted
```

- Removes scattered `if logger is not None` checks. **Don't use** if "absent" must be
  distinguishable from "present but no-op".

---

## Pattern selection cheat sheet

| You see... | Reach for | Not if... |
|---|---|---|
| Interchangeable algorithms chosen at runtime | **Strategy** | there are only 2 fixed cases → just `if/else` |
| Create one of several subtypes by input | **Factory** | only one concrete type exists |
| Object with many optional fields | **Builder** | a dataclass + defaults suffices (esp. Python) |
| Exactly one shared instance | **Singleton** | you can pass the object in (DI) instead |
| Add stackable behavior at runtime | **Decorator** | behavior is fixed → subclass or compose |
| Incompatible third-party interface | **Adapter** | you control both sides → just align them |
| One change notifies many | **Observer** | one fixed listener → direct call |
| Behavior differs per internal state | **State** | 2 states → a boolean + `if` is fine |
| Undo / queue / log operations | **Command** | no undo/queue need |
| Sequential handlers, each may handle/pass | **Chain of Responsibility** | fixed 2-step check |
| Fixed skeleton, variable steps | **Template Method** | you want runtime swapping → Strategy |
| Simplify a complex subsystem | **Facade** | there's only one subsystem already |
| Control access / lazy-load / cache | **Proxy** | you want to *add behavior* → Decorator |
| Tree of leaves + containers | **Composite** | structure is flat |
| Avoid null checks | **Null Object** | absence must be detectable |

> Keep the judgement front-and-center: **the simplest design that meets the requirements and
> stays open to the changes you actually expect.** A pattern you can justify beats three you
> forced in.

## Related

- The common eight + per-pattern trade-offs → [Roadmap → Design Patterns](roadmap.md#6-design-patterns)
- Compact runnable examples → [Low-Level Design Guide](LowLevelDesign.md)
- "Which pattern?" decision tree → [LLD Mental Models](lld-mental-models.md)
- Patterns applied in full solutions → [Worked Problems](worked-problems.md)
