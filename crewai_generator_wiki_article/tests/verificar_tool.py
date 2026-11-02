import time
from crewai_generator_wiki_article.tools.wikipedia_tool import WikipediaTool

print("=" * 60)
print("TESTE 3: chamada real à API")
print("=" * 60)

t = WikipediaTool()
result = t._run("Brasil")
print(f"Tamanho: {len(result)} caracteres")
print("-" * 60)
print(result[:400])
print("=" * 60)

print("\nTESTE 4a: cache")
t0 = time.time()
t._run("Brasil")  # já está no cache
t1 = time.time()
print(f"Chamada em cache: {(t1 - t0) * 1000:.2f} ms")

print("\nTESTE 4b: termo inexistente (fallbacks)")
r = t._run("Xyzabcqwerty12345")
print(r[:300])