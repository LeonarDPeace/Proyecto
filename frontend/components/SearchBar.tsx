"use client";

import { useState } from "react";
import Input from "@/components/ui/Input";

interface SearchBarProps {
  onSearch?: (query: string) => void;
  placeholder?: string;
}

export default function SearchBar({
  onSearch,
  placeholder = "Buscar productos en tu campus...",
}: SearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch && query.trim()) {
      onSearch(query.trim());
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
      <button
        type="submit"
        className="rounded-lg bg-vera-600 px-4 py-2 text-sm font-semibold text-white hover:bg-vera-700 transition-colors"
      >
        Buscar
      </button>
    </form>
  );
}
