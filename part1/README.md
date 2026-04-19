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
