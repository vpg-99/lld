"""
Low-Level Design Interview Template
Incorporates: SOLID Principles, Design Patterns, Best Practices
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
import threading


# ============================================================================
# ENUMS - Define all status/type enumerations
# ============================================================================
class EntityStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"


# ============================================================================
# MODELS - Core domain entities (Single Responsibility Principle)
# ============================================================================
class BaseEntity:
    """Base class for all entities with common attributes"""

    def __init__(self, id: str):
        self.id = id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update_timestamp(self):
        self.updated_at = datetime.now()


class User(BaseEntity):
    """Example entity - Replace with your domain model"""

    def __init__(self, id: str, name: str, email: str):
        super().__init__(id)
        self.name = name
        self.email = email
        self.status = EntityStatus.ACTIVE


# ============================================================================
# INTERFACES - Define contracts (Interface Segregation Principle)
# ============================================================================
class IRepository(ABC):
    """Generic repository interface"""

    @abstractmethod
    def get_by_id(self, id: str):
        pass

    @abstractmethod
    def save(self, entity):
        pass

    @abstractmethod
    def delete(self, id: str):
        pass


class INotificationService(ABC):
    """Notification service interface (Dependency Inversion Principle)"""

    @abstractmethod
    def send(self, recipient: str, message: str):
        pass


# ============================================================================
# REPOSITORIES - Data access layer (Single Responsibility)
# ============================================================================
class InMemoryRepository(IRepository):
    """Thread-safe in-memory repository implementation"""

    def __init__(self):
        self._storage: Dict[str, any] = {}
        self._lock = threading.Lock()

    def get_by_id(self, id: str):
        with self._lock:
            return self._storage.get(id)

    def save(self, entity):
        with self._lock:
            entity.update_timestamp()
            self._storage[entity.id] = entity

    def delete(self, id: str):
        with self._lock:
            if id in self._storage:
                del self._storage[id]

    def get_all(self) -> List:
        with self._lock:
            return list(self._storage.values())


# ============================================================================
# SINGLETON PATTERN - For system-wide single instance
# ============================================================================
class ConfigManager:
    """Thread-safe singleton for configuration management"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._config = {}
        self._initialized = True

    def set(self, key: str, value: any):
        self._config[key] = value

    def get(self, key: str, default=None):
        return self._config.get(key, default)


# ============================================================================
# FACTORY PATTERN - Object creation
# ============================================================================
class NotificationFactory:
    """Factory for creating notification services"""

    @staticmethod
    def create_notification_service(type: str) -> INotificationService:
        if type == "EMAIL":
            return EmailNotificationService()
        elif type == "SMS":
            return SMSNotificationService()
        raise ValueError(f"Unknown notification type: {type}")


class EmailNotificationService(INotificationService):
    def send(self, recipient: str, message: str):
        print(f"Email sent to {recipient}: {message}")


class SMSNotificationService(INotificationService):
    def send(self, recipient: str, message: str):
        print(f"SMS sent to {recipient}: {message}")


# ============================================================================
# STRATEGY PATTERN - Interchangeable algorithms
# ============================================================================
class IProcessingStrategy(ABC):
    """Strategy interface for processing logic"""

    @abstractmethod
    def process(self, data: any):
        pass


class StandardProcessingStrategy(IProcessingStrategy):
    def process(self, data: any):
        print(f"Standard processing: {data}")


class PremiumProcessingStrategy(IProcessingStrategy):
    def process(self, data: any):
        print(f"Premium processing with extra features: {data}")


# ============================================================================
# OBSERVER PATTERN - Event notification
# ============================================================================
class IObserver(ABC):
    @abstractmethod
    def update(self, event: str, data: any):
        pass


class Subject:
    """Observable subject that notifies observers"""

    def __init__(self):
        self._observers: List[IObserver] = []

    def attach(self, observer: IObserver):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IObserver):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: str, data: any):
        for observer in self._observers:
            observer.update(event, data)


class LoggingObserver(IObserver):
    def update(self, event: str, data: any):
        print(f"[LOG] Event: {event}, Data: {data}")


# ============================================================================
# SERVICE LAYER - Business logic (Open/Closed Principle)
# ============================================================================
class BaseService:
    """Base service with common functionality"""

    def __init__(self, repository: IRepository):
        self.repository = repository
        self.config = ConfigManager()

    def validate(self, entity) -> bool:
        """Override in subclasses for validation logic"""
        return True


class UserService(BaseService):
    """Service handling user operations (Single Responsibility)"""

    def __init__(
        self, repository: IRepository, notification_service: INotificationService
    ):
        super().__init__(repository)
        self.notification_service = notification_service
        self.subject = Subject()

    def create_user(self, id: str, name: str, email: str) -> User:
        user = User(id, name, email)
        if not self.validate(user):
            raise ValueError("Invalid user data")

        self.repository.save(user)
        self.notification_service.send(email, "Welcome!")
        self.subject.notify("USER_CREATED", user)
        return user

    def get_user(self, id: str) -> Optional[User]:
        return self.repository.get_by_id(id)

    def validate(self, user: User) -> bool:
        return user.name and user.email and "@" in user.email


# ============================================================================
# FACADE PATTERN - Simplified interface to complex subsystem
# ============================================================================
class SystemFacade:
    """
    Simplified interface for the entire system
    Use this as the main entry point in interviews
    """

    _instance = None

    def __init__(self):
        self.config = ConfigManager()
        self.user_repository = InMemoryRepository()
        self.notification_service = NotificationFactory.create_notification_service(
            "EMAIL"
        )
        self.user_service = UserService(self.user_repository, self.notification_service)

        # Attach observers
        logging_observer = LoggingObserver()
        self.user_service.subject.attach(logging_observer)

    def create_user(self, id: str, name: str, email: str) -> User:
        return self.user_service.create_user(id, name, email)

    def get_user(self, id: str) -> Optional[User]:
        return self.user_service.get_user(id)


# ============================================================================
# DEMONSTRATION - How to use the template
# ============================================================================
def main():
    """Example usage demonstrating the template"""

    # Initialize system
    system = SystemFacade()

    # Create users
    user1 = system.create_user("1", "Alice", "alice@example.com")
    user2 = system.create_user("2", "Bob", "bob@example.com")

    # Retrieve user
    retrieved_user = system.get_user("1")
    print(f"Retrieved: {retrieved_user.name if retrieved_user else 'None'}")

    # Demonstrate singleton
    config1 = ConfigManager()
    config2 = ConfigManager()
    config1.set("max_users", 100)
    print(f"Singleton test: {config2.get('max_users')}")  # Should print 100


if __name__ == "__main__":
    main()


"""
USAGE GUIDE FOR INTERVIEWS:
============================

1. START: Understand requirements
   - Identify core entities (Users, Orders, Bookings, etc.)
   - Define relationships and operations

2. REPLACE MODELS: 
   - Modify User class or create new entities
   - Update enums for your domain

3. ADD INTERFACES:
   - Define contracts for major operations
   - Follow Interface Segregation Principle

4. IMPLEMENT REPOSITORIES:
   - Use InMemoryRepository or create specialized ones
   - Keep data access separate from business logic

5. CREATE SERVICES:
   - Business logic goes here
   - One service per major entity/feature
   - Inject dependencies (Dependency Inversion)

6. APPLY PATTERNS AS NEEDED:
   - Singleton: System-wide configs, managers
   - Factory: Object creation logic
   - Strategy: Interchangeable algorithms
   - Observer: Event-driven notifications
   - Facade: Simplified system interface

7. DEMONSTRATE:
   - Create a main() function showing key flows
   - Show SOLID principles in action

SOLID PRINCIPLES CHECKLIST:
============================
✓ Single Responsibility: Each class has one reason to change
✓ Open/Closed: Extend via inheritance/composition, not modification
✓ Liskov Substitution: Subtypes can replace base types
✓ Interface Segregation: Small, focused interfaces
✓ Dependency Inversion: Depend on abstractions, not concretions

COMMON LLD PROBLEMS TO PRACTICE:
=================================
- Parking Lot System
- Library Management System
- Hotel Booking System
- Ride Sharing (Uber/Lyft)
- Food Delivery (Swiggy/Zomato)
- Movie Ticket Booking
- ATM System
- Elevator System
- Chess Game
- Splitwise/Expense Sharing
"""
