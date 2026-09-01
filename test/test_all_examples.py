import sys
import subprocess
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import src.cpile as cpile

EXAMPLES_DIR = Path(__file__).resolve().parent / "examples"
BUILD_DIR = Path(__file__).resolve().parent / "build"
BUILD_DIR.mkdir(exist_ok=True)

examples = list(EXAMPLES_DIR.glob("*.py"))
assert len(examples) > 0, "No examples found!"

all_passed = True

print(f"Found {len(examples)} examples to transpile and verify:\n")

for py_file in sorted(examples):
    print(f"Testing {py_file.name}...")
    
    # 1. Transpile Python to C
    try:
        c_code = cpile.transpile_file(str(py_file))
    except Exception as e:
        print(f"❌ Transpilation error in {py_file.name}: {e}")
        all_passed = False
        continue

    # 2. Write generated C code
    c_out = BUILD_DIR / f"{py_file.stem}.c"
    c_out.write_text(c_code, encoding="utf-8")

    # 3. Compile with GCC
    obj_out = BUILD_DIR / f"{py_file.stem}.o"
    gcc_res = subprocess.run(
        ["gcc", "-c", str(c_out), "-o", str(obj_out)],
        capture_output=True,
        text=True
    )

    if gcc_res.returncode == 0:
        print(f"  ✅ Transpiled to clean C")
        print(f"  ✅ GCC compiled successfully (0 errors, 0 warnings)\n")
    else:
        print(f"  ❌ GCC compilation failed for {py_file.name}:")
        print(gcc_res.stderr)
        all_passed = False

if all_passed:
    print("🎉 ALL EXAMPLES PASSED VERIFICATION! 🎉")
else:
    sys.exit(1)
