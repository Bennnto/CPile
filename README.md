# cpile ⚡

✱cpile✱ python code to C code with type annotation, produces readable C code with native C performance

---
## Support Features (0.1.0)
1. Type Mapping : map compatible python type with c type

   
|  Python  type    |   C type         |
|------------------|------------------|
| int (interger)   | int32_t          |
| str (string)     | char*            |
| float (floating point) | double     |
| bool (boolean)   | bool <stdbool.h> |
| None             | void             |


2. Function and Recursion : Full support for typed function signatures and recursive calls (e.g., Fibonacci).
3. Control Flow : Full support `if`, `else`, and `elif` block with proper c scoping and indentation.
4. Loop : Support `while` loop with condition, `for` loop with `range(n)`, `range(start, stop)` and `range(start, stop, step)` 
5. Variable Declaration : Support variable with type declaration and tracking so variable declare once with their c type and reassigned cleanly
6. Arithmetic Operators and Logic : Full Support Binary Operator(`+`, `-`, `*`, `\`, `%`) comparison (`>`, `<`, `<=`, `>=`, `!=`, `==`) logic (`&&`, `||`, `!`)

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
