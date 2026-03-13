# Testing Guide

## Quick Test (CLI)

With the server running, you can hit the API directly:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I sort a list in Python?"}'
```

## Test Messages

These cover all intents, edge cases, ambiguity, and typos:

| #  | Message                                                                                      | Expected Intent |
|----|----------------------------------------------------------------------------------------------|-----------------|
| 1  | how do i sort a list of objects in python?                                                   | code            |
| 2  | explain this sql query for me                                                                | code            |
| 3  | This paragraph sounds awkward, can you help me fix it?                                       | writing         |
| 4  | I'm preparing for a job interview, any tips?                                                 | career          |
| 5  | what's the average of these numbers: 12, 45, 23, 67, 34                                     | data            |
| 6  | Help me make this better.                                                                    | unclear         |
| 7  | I need to write a function that takes a user id... but also i need help with my resume.      | unclear         |
| 8  | hey                                                                                          | unclear         |
| 9  | Can you write me a poem about clouds?                                                        | unclear         |
| 10 | Rewrite this sentence to be more professional.                                               | writing         |
| 11 | I'm not sure what to do with my career.                                                      | career          |
| 12 | what is a pivot table                                                                        | data            |
| 13 | fxi thsi bug pls: for i in range(10) print(i)                                               | code            |
| 14 | How do I structure a cover letter?                                                           | career          |
| 15 | My boss says my writing is too verbose.                                                      | writing         |

## Manual Override Test

Prefix with `@intent` to bypass the classifier:

```
@code Fix this bug: for i in range(10) print(i)
```

## Automated Test Script

Run the included test script to fire all 15 messages through the API:

```bash
python tests/test_router.py
```

This prints the classified intent and confidence for each message and writes results to `route_log.jsonl`.
