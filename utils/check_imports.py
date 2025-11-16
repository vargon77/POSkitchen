# utils/check_imports.py
try:
    from kivymd.uix.button import MDFlatButton, MDRaisedButton
    print("✅ MDFlatButton y MDRaisedButton - OK")
except ImportError as e:
    print(f"❌ Error con buttons: {e}")

try:
    from kivymd.uix.chip import MDChip
    print("✅ MDChip - OK")
except ImportError as e:
    print(f"❌ Error con chip: {e}")

try:
    from kivymd.uix.dialog import MDDialog
    print("✅ MDDialog - OK")
except ImportError as e:
    print(f"❌ Error con dialog: {e}")

try:
    from kivymd.uix.textfield import MDTextField
    print("✅ MDTextField - OK")
except ImportError as e:
    print(f"❌ Error con textfield: {e}")

print(f"🎯 KivyMD version: {__import__('kivymd').__version__}")