export default function ProductDetailPage({
  params,
}: {
  params: { id: string };
}) {
  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900">
        Detalle del Producto
      </h1>
      <p className="mt-2 text-sm text-gray-500">
        ID: {params.id} — Sprint 0 (estructura base).
      </p>

      {/* TODO (Sprint 1): Detalle completo con imágenes, precio, vendedor */}
      <div className="mt-8 rounded-lg border border-dashed border-gray-300 p-8 text-center text-gray-400">
        <p className="text-sm">
          El detalle del producto se implementará en Sprint 1
        </p>
      </div>
    </main>
  );
}
