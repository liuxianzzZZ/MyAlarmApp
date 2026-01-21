import importlib.util
import os
import sys

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(base)
    if root not in sys.path:
        sys.path.insert(0, root)
    target = os.path.join(base, "test_database.py")
    spec = importlib.util.spec_from_file_location("test_database", target)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["test_database"] = mod
    spec.loader.exec_module(mod)
    if hasattr(mod, "setup_module"):
        mod.setup_module()
    mod.test_add_and_query()
    mod.test_check_alarm_once()
    mod.test_check_alarm_daily_advance()
    print("数据库测试通过")

if __name__ == "__main__":
    main()
