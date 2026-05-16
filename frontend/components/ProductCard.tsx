"use client";

import Card from "@/components/ui/Card";
import { motion } from "framer-motion";

interface Product {
  id: string;
  name: string;
  price: number;
  category?: string | null;
  image_urls: string[];
  is_active: boolean;
  stock?: number;
  discount_percentage?: number;
}

interface ProductCardProps {
  product: Product;
  variant?: "grid" | "list";
}

export default function ProductCard({ product, variant = "grid" }: ProductCardProps) {
  const formattedPrice = new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
  }).format(product.price);

  const hasDiscount = product.discount_percentage && product.discount_percentage > 0;
  const originalPrice = hasDiscount 
    ? product.price / (1 - product.discount_percentage! / 100)
    : product.price;

  if (variant === "list") {
    return (
      <motion.div 
        whileHover={{ x: 5 }} 
        transition={{ duration: 0.2 }}
        className="w-full"
      >
        <Card className="flex items-center gap-4 p-3 bg-white/70 backdrop-blur-md border border-white/40 shadow-lg shadow-black/5 rounded-2xl">
          {/* Imagen mini */}
          <div className="h-20 w-20 flex-shrink-0 bg-gray-100 rounded-xl overflow-hidden relative">
            {product.image_urls?.length > 0 ? (
              <img
                src={product.image_urls[0]}
                alt={product.name}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center opacity-40">📦</div>
            )}
            {hasDiscount && (
              <span className="absolute top-1 left-1 bg-red-500 text-white text-[8px] font-bold px-1.5 py-0.5 rounded-full shadow-sm">
                -{product.discount_percentage}%
              </span>
            )}
          </div>

          {/* Info Horizontal */}
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-gray-900 text-sm truncate">{product.name}</h3>
            <div className="mt-1 flex items-center gap-2">
              <p className="text-lg font-black text-vera-700">{formattedPrice}</p>
              {hasDiscount && (
                <p className="text-xs text-gray-400 line-through">
                  {new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", minimumFractionDigits: 0 }).format(originalPrice)}
                </p>
              )}
            </div>
            <div className="mt-1 flex items-center gap-2">
              {product.category && (
                <span className="text-[9px] font-bold text-vera-600 bg-vera-50 px-1.5 py-0.5 rounded uppercase">
                  {product.category}
                </span>
              )}
              {product.stock !== undefined && product.stock > 0 && (
                <span className="text-[10px] text-green-600">
                  {product.stock} disp.
                </span>
              )}
            </div>
          </div>
          
          <div className="text-vera-300">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 18l6-6-6-6" />
            </svg>
          </div>
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div 
      whileHover={{ y: -5, scale: 1.01 }} 
      transition={{ duration: 0.2 }}
      className="h-full"
    >

      <Card className="h-full relative overflow-hidden group bg-white/70 backdrop-blur-md border border-white/40 shadow-xl shadow-black/5">
        {/* Badges */}
        <div className="absolute top-2 right-2 flex flex-col gap-1 z-10 items-end">
          {hasDiscount && (
            <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-md">
              -{product.discount_percentage}%
            </span>
          )}
          {product.stock !== undefined && product.stock === 0 && (
            <span className="bg-gray-800 text-white text-xs font-medium px-2 py-1 rounded-full shadow-md">
              Agotado
            </span>
          )}
        </div>

        {/* Imagen placeholder */}
        <div className="mb-4 flex h-48 w-full items-center justify-center bg-gray-100/50 text-gray-400 overflow-hidden relative rounded-t-xl -mt-6 -mx-6">
          {product.image_urls?.length > 0 ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={product.image_urls[0]}
              alt={product.name}
              className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          ) : (
            <span className="text-4xl opacity-50">📦</span>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>

        {/* Info */}
        <div className="px-1">
          <h3 className="font-bold text-gray-900 line-clamp-2 leading-tight">{product.name}</h3>
          
          <div className="mt-2 flex flex-wrap gap-1">
            {product.category && (
              <span className="inline-block rounded-md bg-vera-50 px-2 py-0.5 text-[10px] font-semibold text-vera-700 tracking-wide uppercase">
                {product.category}
              </span>
            )}
          </div>
          
          <div className="mt-3 flex items-baseline gap-2">
            <p className="text-xl font-black text-vera-700">{formattedPrice}</p>
            {hasDiscount && (
              <p className="text-sm text-gray-400 line-through">
                {new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", minimumFractionDigits: 0 }).format(originalPrice)}
              </p>
            )}
          </div>
          
          {product.stock !== undefined && product.stock > 0 && (
            <p className="mt-2 text-xs text-green-600 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              {product.stock} disponibles
            </p>
          )}
        </div>
      </Card>
    </motion.div>
  );
}
