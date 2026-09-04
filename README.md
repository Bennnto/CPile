# cpile ⚡

[![PyPI version](https://img.shields.io/pypi/v/cpile.svg)](https://pypi.org/project/cpile/)
[![Python versions](https://img.shields.io/pypi/pyversions/cpile.svg)](https://pypi.org/project/cpile/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**cpile** transpiles type-annotated Python code into clean, readable C99 that compiles with GCC for native performance.

Write Python with standard type hints, get human-readable C code, and compile to native binaries without touching boilerplate C headers or manual memory setups.

---

## Installation

```bash
pip install cpile
```

*Requirements: Python >= 3.13, GCC (for native compilation).*

---

## Command Line Interface (CLI)

`cpile` comes with a command-line tool to transpile and build directly from your terminal:

```bash
# 1. Transpile Python to C and print to terminal
cpile transpile script.py

# 2. Transpile and save directly to a .c file
cpile transpile script.py -o output.c

# 3. Transpile and compile directly into an executable binary using GCC
cpile build script.py -o myapp
./myapp
```

---

## Quickstart (Python API)

You can also use `cpile` directly inside your Python projects:

```python
import cpile

code = """
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""

# Transpile Python source string to C
c_code = cpile.transpile(code)
print(c_code)
```

**Generated C Output:**
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

int32_t fibonacci (int32_t n) {
  if (n <= 1) {
    return n;
  }
  return fibonacci(n - 1) + fibonacci(n - 2);
}
```

---

## Supported Features

### 1. Type System & Mapping
Standard Python type hints map directly to fixed-width C types:

| Python Type | C99 Equivalent |
|---|---|
| `int` | `int32_t` (`<stdint.h>`) |
| `float` | `double` |
| `str` | `char*` |
| `bool` | `bool` (`<stdbool.h>`) |
| `None` | `void` |

### 2. Classes as C Structs
Define custom data types using Python classes with annotations:
```python
class Vector:
    x: int
    y: int

v: Vector = Vector(10, 20)
v.x = 30
```
Transpiles to:
```c
typedef struct {
  int32_t x;
  int32_t y;
} Vector;

Vector v = (Vector){10, 20};
v.x = 30;
```

### 3. Arrays & 2D Arrays
Supports both 1D and 2D arrays with fixed size detection:
```python
matrix: list[list[int]] = [[1, 2], [3, 4]]
```
Transpiles to:
```c
int32_t matrix[2][2] = {{1, 2}, {3, 4}};
```

### 4. Control Flow & Loops
* `if`, `elif`, and `else` blocks with proper C indentation and scoping.
* `while` loops and `for` loops using `range(stop)`, `range(start, stop)`, and `range(start, stop, step)`.
* `break` and `continue` statement support.

### 5. Strings & Comparison
Equality checks on strings automatically generate clean `strcmp` calls:
```python
def is_admin(user: str) -> bool:
    if user == "root":
        return True
    return False
```
Transpiles to:
```c
bool is_admin (char* user) {
  if (strcmp(user, "root") == 0) {
    return true;
  }
  return false;
}
```

### 6. Math Functions & Built-ins
Supports standard mathematical functions (`sqrt`, `pow`, `abs`, `fabs`, `floor`, `ceil`) from `<math.h>` automatically.

### 7. Ternary & Compound Operators
* Augmented assignments: `+=`, `-=`, `*=`, `/=`
* One-line ternary expressions: `max_val: int = a if a > b else b` → `int32_t max_val = a > b ? a : b;`

---

## Project Structure

```text
cpile/
├── src/
│   └── cpile/
│       ├── __init__.py      # Package export (transpile, transpile_file, compile_c)
│       ├── analyzer.py      # AST visitor for type analysis and symbol table
│       ├── cli.py           # Command line interface (cpile transpile / build)
│       ├── codegen.py       # AST-to-C code generator
│       ├── errors.py        # Custom transpilation exception classes
│       ├── transpiler.py    # Public API & GCC compilation integration
│       └── types.py         # Python-to-C type mappings and type inference
├── test/
│   ├── examples/            # End-to-end Python test examples
│   │   ├── arrays.py        # 1D array operations
│   │   ├── bubble_sort.py   # In-place sorting algorithm
│   │   ├── conditions.py    # Branching & logic operators
│   │   ├── fibonacci.py     # Recursion benchmark
│   │   ├── loops.py         # While & for range iterations
│   │   ├── math_ops.py      # Math functions (<math.h>)
│   │   ├── strings.py       # String operations & comparisons
│   │   ├── structs.py       # Class-to-struct transpilation
│   │   └── swap.py          # Value swaps
│   ├── test_all_examples.py # End-to-end transpile + GCC compile test runner
│   ├── test_analyze.py      # Analyzer & symbol table unit tests
│   ├── test_array.py        # Array code generation tests
│   ├── test_codegen.py      # Core generator tests
│   ├── test_str_comp.py     # String comparison tests
│   ├── test_struct.py       # Struct definition tests
│   └── test_type.py         # Type mapping & inference tests
├── pyproject.toml           # Packaging metadata & entry points
└── README.md
```

---

## Running Verification Tests

Run the full end-to-end test suite to transpile all 9 examples and compile each with GCC:

```bash
python3 test/test_all_examples.py
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
