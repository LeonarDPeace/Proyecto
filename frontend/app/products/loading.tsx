"use client";

export default function Loading() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Skeleton for Header */}
      <div className="h-8 w-48 bg-gray-200 rounded animate-pulse mb-2"></div>
      <div className="h-4 w-64 bg-gray-100 rounded animate-pulse mt-2"></div>

      {/* Skeleton for Grid */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="rounded-lg border border-gray-100 p-4 shadow-sm flex flex-col h-full">
            <div className="aspect-[4/3] w-full bg-gray-200 rounded-md animate-pulse mb-4"></div>
            <div className="flex-1">
              <div className="h-5 w-3/4 bg-gray-200 rounded animate-pulse mb-3"></div>
              <div className="h-4 w-1/2 bg-gray-100 rounded animate-pulse mb-4"></div>
            </div>
            <div className="h-6 w-1/3 bg-gray-300 rounded animate-pulse mt-auto"></div>
          </div>
        ))}
      </div>
    </main>
  );
}
