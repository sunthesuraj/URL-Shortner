# 🧠 Approach Summary: URL Shortener Service

This project followed a **structured and iterative development approach**, prioritizing robustness, adherence to best practices, and thorough testing. The process mirrored a real-world development cycle, progressing from initial design to implementation, debugging, and final verification.

---

## 1. 🔧 Architectural Foundation

The initial design adopted a **modular structure** to ensure separation of concerns — a key principle for building scalable and maintainable applications.

* `app/main.py`: Contained the core application logic, including route definitions and request handling.
* `app/models.py`: Managed data storage. A key decision here was to use `threading.Lock` for the in-memory dictionary to make it thread-safe, preventing race conditions during concurrent requests.
* `app/utils.py`: Contained utility functions like short code generation and URL validation, keeping the main app clean and focused.

🧹 **Refactor Note**:
To resolve import path issues during testing, all logic was consolidated into a single `app/main.py` file. This pragmatic move simplified the structure for the assignment's scale, while retaining core logic.

---

## 2. 🛠️ Key Implementation Choices

Several technical decisions enhanced the reliability and maintainability of the code:

### ✅ URL Validation

* Instead of complex regular expressions, the `validators` library was used — a best practice leveraging well-tested tools for common validation tasks.

### ✅ Short Code Generation

* Used `random.choices` to generate a 6-character alphanumeric code efficiently.
* Wrapped the generation in a `while` loop to avoid collisions, ensuring all short codes remain unique.

### ✅ Centralized Error Handling

* Introduced a custom `ApiError` exception.
* Paired it with Flask’s `@app.errorhandler` decorators to ensure **consistent and clean JSON error responses** across all endpoints — enhancing developer experience for API consumers.

---

## 3. 🔍 Testing & Debugging Process

Testing played a central role in reaching a stable and verified solution.

### 🧪 Manual Testing (curl & Postman)

Initial verification was done manually, revealing several environment-specific issues:

* **curl on PowerShell**: Resolved by using `curl.exe` to avoid command conflicts.
* **JSON quoting in PowerShell**: Fixed by escaping nested quotes.
* **404/500 Errors**: Diagnosed via server logs, resolving issues like missing imports and outdated code.

### 🧪 Automated Testing (pytest)

A full **pytest test suite** was developed to cover both happy paths and edge cases.

#### Key Fixes During Test Debugging:

* **ModuleNotFoundError**: Solved by creating a `pytest.ini` file to correctly configure the `PYTHONPATH`.
* **AttributeError (`'bool' object has no attribute 'get'`)**: Tracked to incorrect test setup where `app.config = True` mistakenly overwrote the config dictionary. Fixed by setting `app.config['TESTING'] = True`.

---

