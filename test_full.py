# test_full.py
print("=== TESTE COMPLETO DE IMPORTAÇÃO ===\n")

print("1. Testando config...")
try:
    from config import settings
    print(f"✅ Config OK - API: {settings.RAPID_API_HOST}")
except Exception as e:
    print(f"❌ Config ERROR: {e}")

print("\n2. Testando services...")
try:
    from services import LoteriaAPI, AIEngine, JogoGenerator, KPICalculator
    print("✅ Todos os serviços importados")
    
    # Teste cada serviço
    api = LoteriaAPI()
    print(f"✅ LoteriaAPI criado: {api}")
    
    ai = AIEngine()
    print(f"✅ AIEngine criado: {ai}")
    
    gerador = JogoGenerator()
    print(f"✅ JogoGenerator criado: {gerador}")
    
    kpi = KPICalculator()
    print(f"✅ KPICalculator criado: {kpi}")
    
except Exception as e:
    print(f"❌ Services ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Testando utils...")
try:
    from utils import Formatters, validar_dezenas
    print("✅ Utils importados")
except Exception as e:
    print(f"❌ Utils ERROR: {e}")

print("\n4. Testando assets...")
try:
    from assets.components import UIComponents
    print("✅ Components importados")
except Exception as e:
    print(f"❌ Assets ERROR: {e}")