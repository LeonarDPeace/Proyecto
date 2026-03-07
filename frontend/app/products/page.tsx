export default function ProductsPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-bold text-gray-900">Catálogo</h1>
      <p className="mt-2 text-sm text-gray-500">
        Productos disponibles en tu campus — Sprint 0 (estructura base).
      </p>

      {/* TODO (Sprint 1): Grid de ProductCard con datos reales */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center text-gray-400">
          <p className="text-sm">Los productos aparecerán aquí en Sprint 1</p>
        </div>
      </div>
    </main>
  );
}
