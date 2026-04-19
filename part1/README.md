# HBnB Evolution - Technical Design

## 0. High-Level Package Diagram

### Architecture Overview
The HBnB application follows a **three-layer architecture** to ensure a clean separation of concerns:

1. **Presentation Layer**: Handles API requests and user interactions.
2. **Business Logic Layer**: Contains the core entities (User, Place, etc.) and logic.
3. **Persistence Layer**: Manages data storage and retrieval.

### Diagram
classDiagram
    namespace Presentation_Layer {
        class Services_API {
            +UserEndpoints
            +PlaceEndpoints
            +ReviewEndpoints
            +AmenityEndpoints
        }
    }

    namespace Business_Logic_Layer {
        class HBnBFacade {
            <<Interface>>
            +create_user(data)
            +get_place_details(id)
            +register_review(review)
        }
        class Models {
            +User
            +Place
            +Review
            +Amenity
        }
    }

    namespace Persistence_Layer {
        class Repository {
            +Save(obj)
            +Get(id)
            +Delete(id)
        }
        class Database {
            <<Storage>>
        }
    }

    Services_API --> HBnBFacade : Unified Calls
    HBnBFacade --> Models : Manages
    HBnBFacade --> Repository : Coordinates Persistence
    Repository --> Database : SQL/NoSQL Operations

### The Facade Pattern
The communication between the Presentation and Business Logic layers is handled via a **Facade**. This pattern provides a unified interface, simplifying the API's interaction with the backend and allowing internal logic changes without affecting external endpoints.

---

## 1. Business Logic Class Diagram

### Entities Overview
The Business Logic layer is designed using an Object-Oriented approach with a central **BaseModel** to ensure data consistency across all entities.

* **BaseModel**: Parent class providing `id`, `created_at`, and `updated_at`.
* **User**: Handles profile information and links to owned places and written reviews.
* **Place**: The core entity for listings, linked to an owner, multiple reviews, and a list of amenities.
* **Review**: Connects a User to a Place with a rating and comment.
* **Amenity**: Standalone features (like "WiFi" or "Pool") that can be associated with multiple places.

### Diagram
```mermaid
classDiagram
    class BaseModel {
        +UUID4 id
        +datetime created_at
        +datetime updated_at
        +save()
        +update(data)
    }

    class User {
        +string first_name
        +string last_name
        +string email
        +string password
        +bool is_admin
        +register()
        +login()
    }

    class Place {
        +string title
        +string description
        +float price
        +float latitude
        +float longitude
        +add_amenity(amenity)
        +add_review(review)
    }

    class Review {
        +int rating
        +string comment
        +edit_review(text, rating)
    }

    class Amenity {
        +string name
        +string description
    }

    BaseModel <|-- User : Inheritance
    BaseModel <|-- Place : Inheritance
    BaseModel <|-- Review : Inheritance
    BaseModel <|-- Amenity : Inheritance

    User "1" --> "0..*" Place : Owns
    User "1" --> "0..*" Review : Writes
    Place "1" *-- "0..*" Review : Contains
    Place "0..*" -- "0..*" Amenity : Has (Many-to-Many)


---

## 2. Sequence Diagrams

This section illustrates the dynamic interaction between the Presentation, Business Logic, and Persistence layers for four key system operations using the Facade pattern.

### 2.1 User Registration
**Description:** A new user signs up for an account. The system validates the email uniqueness before creating the record.

```mermaid
sequenceDiagram
    participant Client
    participant API as Presentation Layer (API)
    participant Facade as Business Logic (Facade)
    participant DB as Persistence Layer (Database)

    Client->>API: POST /users (name, email, password)
    API->>Facade: register_user(data)
    Facade->>DB: get_user_by_email(email)
    DB-->>Facade: None (Email is unique)
    Facade->>DB: save(user_instance)
    DB-->>Facade: Success
    Facade-->>API: User Data (UUID)
    API-->>Client: 201 Created

### 2.2 Place Creation

**Description:** An authorized user creates a new rental listing. The flow ensures the owner is valid before listing the place.
```mermaid
sequenceDiagram
    participant Client
    participant API as Presentation Layer (API)
    participant Facade as Business Logic (Facade)
    participant DB as Persistence Layer (Database)

    Client->>API: POST /places (title, price, owner_id)
    API->>Facade: create_place(data)
    Facade->>DB: get_user(owner_id)
    DB-->>Facade: User Instance Found
    Facade->>DB: save(place_instance)
    DB-->>Facade: Success
    Facade-->>API: Place Data (UUID)
    API-->>Client: 201 Created

### 2.3 Review Submission

**Description:** A user submits a rating and comment for a place. The system links the review to both the user and the place.
```mermaid
sequenceDiagram
    participant Client
    participant API as Presentation Layer (API)
    participant Facade as Business Logic (Facade)
    participant DB as Persistence Layer (Database)

    Client->>API: POST /places/{id}/reviews (user_id, rating, comment)
    API->>Facade: add_review(place_id, data)
    Facade->>DB: get_place(place_id)
    DB-->>Facade: Place Valid
    Facade->>DB: get_user(user_id)
    DB-->>Facade: User Valid
    Facade->>DB: save(review_instance)
    DB-->>Facade: Success
    Facade-->>API: Review Data (UUID)
    API-->>Client: 201 Created

### 2.4 Fetching a List of Places

**Description:** A user requests all available listings. The flow illustrates a simple retrieval process through the architecture.
```mermaid
sequenceDiagram
    participant Client
    participant API as Presentation Layer (API)
    participant Facade as Business Logic (Facade)
    participant DB as Persistence Layer (Database)

    Client->>API: GET /places
    API->>Facade: get_all_places()
    Facade->>DB: get_all_records("Place")
    DB-->>Facade: List of Place Entities
    Facade-->>API: List of Dictionaries (DTOs)
    API-->>Client: 200 OK (JSON List)

---

### Final Compilation Notes

This document provides the foundational design for the HBnB project. By adhering to the **Facade pattern**  and the **layered architecture** outlined here, the development team ensures that the code remains modular, easy to refactor, and ready for future persistence upgrades (e.g., transitioning from in-memory storage to a relational database). 
