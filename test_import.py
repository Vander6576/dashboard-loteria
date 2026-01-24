# test_import.py
import sys
print(f"Python path: {sys.path[:3]}")

print("\n1. Testando importação direta da classe Settings:")
try:
    from config.settings import Settings
    print("✅ from config.settings import Settings - OK")
    test_settings = Settings()
    print(f"   RAPID_API_HOST: {test_settings.RAPID_API_HOST}")
except Exception as e:
    print(f"❌ ERRO: {e}")

print("\n2. Testando importação do pacote config:")
try:
    from config import settings
    print("✅ from config import settings - OK")
    print(f"   RAPID_API_HOST: {settings.RAPID_API_HOST}")
except Exception as e:
    print(f"❌ ERRO: {e}")

print("\n3. Verificando arquivo config/__init__.py:")
try:
    import config
    print(f"✅ Módulo config carregado: {config.__file__}")
    print(f"   Tem atributo 'settings'? {hasattr(config, 'settings')}")
except Exception as e:
    print(f"❌ ERRO: {e}")