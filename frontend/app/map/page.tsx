export default function MapPage() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-bold text-gray-900">
        Mapa del Campus
      </h1>
      <p className="mt-2 text-sm text-gray-500">
        Encuentra vendedores cerca de ti — UAO, Cali.
      </p>

      {/* TODO (Sprint 1): MapView con Leaflet + OpenStreetMap */}
      <div className="mt-8 flex h-96 items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50">
        <div className="text-center text-gray-400">
          <p className="text-lg font-medium">🗺️ Mapa Interactivo</p>
          <p className="mt-2 text-sm">
            Leaflet + OpenStreetMap se implementará en Sprint 1
          </p>
          <p className="mt-1 text-xs">
            Coordenadas UAO: 3.3516, -76.5320
          </p>
        </div>
      </div>
    </main>
  );
}
