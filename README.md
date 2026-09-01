# cpile ⚡

> Transpile type-annotated Python to clean, human-readable C code with native performance.

Unlike existing Python-to-C tools that generate thousands of lines of unreadable machine code, **cpile** produces C code that looks like a human developer wrote it by hand.

---

## Features (Phase 1)

- ✅ **Type Mapping**: `int` $\rightarrow$ `int32_t`, `float` $\rightarrow$ `double`, `bool` $\rightarrow$ `bool`, `str` $\rightarrow$ `char*`, `None`/`void` $\rightarrow$ `void`
- ✅ **Functions & Recursion**: Full support for typed function signatures and recursive calls (e.g., Fibonacci).
- ✅ **Control Flow**: `if`, chained `elif`, and `else` blocks with proper C scoping and indentation.
- ✅ **Loops**: `for` loops with `range(stop)`, `range(start, stop)`, and `range(start, stop, step)`, plus `while` loops.
- ✅ **Variable Handling**: Smart declaration tracking so variables are declared once with their C type and reassigned cleanly.
- ✅ **Arithmetic & Logic**: Full binary operators (`+`, `-`, `*`, `/`, `%`), comparisons (`==`, `!=`, `<`, `>`, `<=`, `>=`), and logical operators (`&&`, `||`, `!`).

---

## Project Structure

```
cpile/
├── src/
│   └── cpile/
│       ├── __init__.py      # Package export (transpile, transpile_file, compile_c)
│       ├── types.py         # Python-to-C type mapping and format specifiers
│       ├── analyzer.py      # AST visitor for type analysis and symbol table
│       ├── codegen.py       # C code generator
│       └── transpiler.py    # Public API & GCC compilation integration
├── test/
│   ├── examples/            # Sample Python programs to transpile
│   │   ├── fibonacci.py
│   │   ├── loops.py
│   │   ├── math_ops.py
│   │   └── conditions.py
│   ├── test_all_examples.py # End-to-end verification suite
│   ├── test_type.py         # Unit tests for types
│   ├── test_analyze.py      # Unit tests for analyzer
│   └── test_codegen.py      # Unit tests for code generator
├── pyproject.toml           # Package configuration
└── README.md
```

---

## Quickstart

### 1. Transpile a Python string
```python
import cpile

code = """
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"""

c_code = cpile.transpile(code)
print(c_code)
```

**Output:**
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

int32_t fibonacci (int32_t n) {
  if (n <= 1) {
    return n;
  }
  return fibonacci(n - 1) + fibonacci(n - 2);
}
```

### 2. Transpile a Python file
```python
import cpile

c_code = cpile.transpile_file("test/examples/loops.py")
```

---

## Running Verification Tests

Run the full verification suite to transpile all examples and compile each one with `gcc`:

```bash
python3 test/test_all_examples.py
```

All examples are transpiled into `test/build/` and compiled to native `.o` binaries using `gcc`.
