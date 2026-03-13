"use client";

export default function LoadingDetails() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
      {/* Title & Badge */}
      <div className="h-10 w-3/4 bg-gray-200 rounded animate-pulse mb-4"></div>
      <div className="h-6 w-1/4 bg-gray-100 rounded animate-pulse mb-8"></div>

      {/* Image Gallery */}
      <div className="aspect-[16/9] w-full bg-gray-200 rounded-xl animate-pulse mb-8"></div>
      
      {/* Description */}
      <div className="space-y-3 mb-8">
        <div className="h-4 w-full bg-gray-100 rounded animate-pulse"></div>
        <div className="h-4 w-5/6 bg-gray-100 rounded animate-pulse"></div>
        <div className="h-4 w-4/6 bg-gray-100 rounded animate-pulse"></div>
      </div>

      {/* Pricing and Action */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between border-t border-gray-100 pt-6">
        <div className="h-8 w-32 bg-gray-200 rounded animate-pulse"></div>
        <div className="h-12 w-full sm:w-48 bg-blue-200 rounded-lg animate-pulse"></div>
      </div>
    </main>
  );
}
