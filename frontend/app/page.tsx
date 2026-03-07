export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      {/* Hero */}
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold tracking-tight text-vera-700 sm:text-5xl">
          Vera<span className="text-vera-500">Market</span>
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Compra y vende dentro de tu campus universitario.
          <br />
          Conecta con emprendedores verificados en Cali, Colombia.
        </p>

        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:justify-center">
          <a
            href="/products"
            className="rounded-lg bg-vera-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-vera-700 transition-colors"
          >
            Explorar Catálogo
          </a>
          <a
            href="/map"
            className="rounded-lg border border-vera-300 px-6 py-3 text-sm font-semibold text-vera-700 hover:bg-vera-50 transition-colors"
          >
            Ver Mapa del Campus
          </a>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-16 text-center text-xs text-gray-400">
        <p>
          VeraMarket &copy; {new Date().getFullYear()} — Sprint 0 (MVP)
        </p>
        <p className="mt-1">
          Campus piloto: Universidad Autónoma de Occidente (UAO)
        </p>
      </footer>
    </main>
  );
}
