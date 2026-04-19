# Holberton School HBnB – Documentation

# TASK 0 - High-Level Package Diagram


Overview

This document presents a high-level package diagram of the HBnB application. The diagram illustrates a three-layer architecture and shows how these layers communicate using the Facade design pattern.

The goal is to provide a clear and structured view of how the system is organized and how its components interact.

Architecture Overview

The HBnB application is built using a layered architecture with three main layers:

Presentation Layer
Business Logic Layer
Persistence Layer

Each layer has its own responsibility and communicates with other layers in a controlled way.

▫️Layer Descriptions


1. Presentation Layer

This is the layer that users interact with directly. It includes API endpoints and Services.

When a user sends a request (for example, creating a user or viewing places), it is received by this layer first. Then the request is passed to the system through the Facade, which acts as the main entry point.


2. Business Logic Layer

This is the core of the application. It defines how the system works and what rules are applied.

It includes:
User
Place
Review
Amenity

In this layer:

Business rules are applied
Data is validated
System logic is handled


3. Persistence Layer

This layer is responsible for storing and retrieving data. It communicates directly with the database.

It includes:

Repository classes (e.g., UserRepository, PlaceRepository)

Its main tasks:

Save data to the database
Retrieve data when needed


▫️ Facade Pattern

The Facade pattern simplifies communication between layers by providing a single interface.

Instead of the Presentation Layer directly communicating with the Business Logic Layer, all requests go through the Facade.

The Facade works like a middle layer that:

Receives requests
Sends them to the correct component
Hides internal complexity


Benefits
Provides one single entry point
Makes the system easier to understand
Improves code organization
Reduces dependency between layers


Communication Flow
The user sends a request to the Presentation Layer
The request goes to the Facade
The Facade calls the Business Logic Layer
The Business Logic Layer interacts with the Persistence Layer
The result is returned back to the user through the same path



# Package Diagram

```mermaid
classDiagram

class PresentationLayer {
    +API Endpoints
    +Services
}

class Facade {
    +create_User()
    +get_Places()
    +add_Review()
    +add_Amenity()
}

class BusinessLogicLayer {
    +User
    +Place
    +Review
    +Amenity
}

class PersistenceLayer {
    +User-Repository
    +Place-Repository
    +Review-Repository
    +Amenity-Repository
}

PresentationLayer --> Facade : Uses
Facade --> BusinessLogicLayer : Handles business logic
BusinessLogicLayer --> PersistenceLayer : Database operations

```

# TASK 1 - Business Logic Layer

Overview

This document describes the Business Logic layer of the HBnB application. It presents a UML class diagram that models the core entities of the system, their attributes, methods, and relationships.

The main goal is to clearly represent how the business logic is structured and how the main entities interact with each other.


Business Logic Layer

The Business Logic layer contains the main entities of the application:

User
Place
Review
Amenity

These entities represent the core functionality of the system and define the main business rules.

## Class Diagram
```mermaid
classDiagram

class BaseModel {
    +UUID4 id
    +DateTime created_at
    +DateTime updated_at
    +save()
    +update(data)
}

class User {
    +String first_name
    +String last_name
    +String email
    +String password
    +Boolean is_admin
    +register()
    +update_profile()
}

class Place {
    +String title
    +String description
    +Float price
    +Float latitude
    +Float longitude
    +UUID4 owner_id
    +create()
    +update()
}

class Review {
    +Int rating
    +String comment
    +UUID4 place_id
    +UUID4 user_id
    +post()
}

class Amenity {
    +String name
    +String description
    +create()
}

%% Inheritance (clean top-down flow)
BaseModel <|-- User
BaseModel <|-- Place
BaseModel <|-- Review
BaseModel <|-- Amenity

%% Relationships (grouped logically)
User "1" --> "0..*" Place : owns
User "1" --> "0..*" Review : writes

Place "1" --> "0..*" Review : has
Place "0..*" -- "0..*" Amenity : includes

```

# TASK 2 - API Calls
Overview

This document presents two main API flows in the HBnB application using sequence diagrams.
Each diagram illustrates how the Presentation, Business Logic, and Persistence layers interact with each other through the Facade pattern.

The goal is to clearly show the request flow, from the user request to data processing and response return.

# User Registration flow

```mermaid
sequenceDiagram

participant User
participant API
participant BusinessLogic
participant Database

User->>API: POST /users (register)
API->>BusinessLogic: validate & create user
BusinessLogic->>Database: save user
Database-->>BusinessLogic: confirmation
BusinessLogic-->>API: success
API-->>User: 201 Created

```

# Place Creation

```mermaid
sequenceDiagram

participant User
participant API
participant Facade
participant BusinessLogic
participant Database

User->>API: POST /places
API->>Facade: createPlace(data)
Facade->>BusinessLogic: validate place
BusinessLogic->>Database: save place
Database-->>BusinessLogic: OK
BusinessLogic-->>Facade: place created
Facade-->>API: success
API-->>User: 201 Created
```

# Review Submission Flow

```mermaid
sequenceDiagram

participant User
participant API
participant BusinessLogic
participant Database

User->>API: Send Review (Rating, Comment)
API->>BusinessLogic: Check IDs
BusinessLogic->>Database: Save Review
Database-->>BusinessLogic: Success
BusinessLogic-->>API: Review Added
API-->>User: Thank you for your review!

```

# Fetching a List of Places
```mermaid 
sequenceDiagram

participant User
participant API
participant Facade
participant BusinessLogic
participant Database

User->>API: GET /places
API->>Facade: getPlaces(filters)
Facade->>BusinessLogic: fetch data
BusinessLogic->>Database: query places
Database-->>BusinessLogic: results
BusinessLogic-->>Facade: places list
Facade-->>API: response
API-->>User: 200 OK + data

