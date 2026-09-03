#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

bool is_admin (char* user) {
  if (user == "root") {
    return true;
  }
  return false;
}
