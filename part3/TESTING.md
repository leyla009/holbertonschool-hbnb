# HBnB Part 2: Testing Report

## Environment
Python 3.14, Flask, flask-restx. Run from `part2/`. Tools: cURL, Swagger UI (`/api/v1/`), unittest.

## Automated tests
Command: `python -m unittest discover -s tests -v`
Result: <N tests, N passed, N failed>

## Manual tests (cURL)
| # | Endpoint | Input | Expected | Actual | Result |
|---|----------|-------|----------|--------|--------|
| 1 | POST /users/ | valid user | 201 | | |
| 2 | POST /users/ | duplicate email | 400 | | |
| 3 | POST /users/ | invalid email | 400 | | |
| 4 | GET /users/<id> | unknown id | 404 | | |
| 5 | PUT /users/<id> | new first_name | 200 | | |
| 6 | POST /amenities/ | empty name | 400 | | |
| 7 | POST /places/ | price -5 | 400 | | |
| 8 | POST /places/ | latitude 120 | 400 | | |
| 9 | POST /places/ | unknown owner_id | 400 | | |
| 10 | GET /places/<id> | valid id | 200 with owner and amenities | | |
| 11 | POST /reviews/ | rating 9 | 400 | | |
| 12 | POST /reviews/ | unknown place_id | 400 | | |
| 13 | DELETE /reviews/<id> | existing, then again | 200, then 404 | | |
| 14 | GET /places/<id>/reviews | unknown place | 404 | | |

## Validation rules
(table from the section above)

## Swagger
Screenshots: <paste>

## Known limitations
- Data is in memory and resets on restart (persistence arrives in Part 3).
- A PUT with one valid and one invalid field may apply the valid one before returning 400.
- No authentication yet (Part 3).
