"use client";

import { useEffect, useState } from "react";
import Input from "@/components/ui/Input";

interface SearchBarProps {
  onSearch?: (query: string) => void;
  onSmartSearch?: (query: string) => void;
  placeholder?: string;
  value?: string;
  onChange?: (query: string) => void;
  loading?: boolean;
  smartLoading?: boolean;
  onClear?: () => void;
  smartLabel?: string;
}

export default function SearchBar({
  onSearch,
  onSmartSearch,
  placeholder = "Buscar productos en tu campus...",
  value,
  onChange,
  loading = false,
  smartLoading = false,
  onClear,
  smartLabel = "Busqueda inteligente",
}: SearchBarProps) {
  const [internalQuery, setInternalQuery] = useState(value ?? "");

  useEffect(() => {
    if (typeof value === "string") {
      setInternalQuery(value);
    }
  }, [value]);

  const query = typeof value === "string" ? value : internalQuery;

  const setQuery = (nextValue: string) => {
    if (typeof value !== "string") {
      setInternalQuery(nextValue);
    }
    onChange?.(nextValue);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch && query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleSmartSearch = () => {
    if (onSmartSearch && query.trim()) {
      onSmartSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="flex-1"
      />
      {query.trim() && onClear && (
        <button
          type="button"
          onClick={onClear}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Limpiar
        </button>
      )}
      <button
        type="submit"
        disabled={loading}
        className="rounded-lg bg-vera-600 px-4 py-2 text-sm font-semibold text-white hover:bg-vera-700 transition-colors"
      >
        {loading ? "Buscando..." : "Buscar"}
      </button>
      {onSmartSearch && (
        <button
          type="button"
          onClick={handleSmartSearch}
          disabled={loading || smartLoading}
          className="rounded-lg border border-vera-200 bg-white px-4 py-2 text-sm font-semibold text-vera-700 hover:bg-vera-50 transition-colors"
        >
          {smartLoading ? "Analizando..." : smartLabel}
        </button>
      )}
    </form>
  );
}
