import Card from "@/components/ui/Card";

interface Product {
  id: string;
  name: string;
  price: number;
  category?: string | null;
  image_urls: string[];
  is_active: boolean;
}

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const formattedPrice = new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
  }).format(product.price);

  return (
    <Card>
      {/* Imagen placeholder */}
      <div className="mb-3 flex h-40 items-center justify-center rounded-md bg-gray-100 text-gray-400">
        {product.image_urls.length > 0 ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={product.image_urls[0]}
            alt={product.name}
            className="h-full w-full rounded-md object-cover"
          />
        ) : (
          <span className="text-3xl">📦</span>
        )}
      </div>

      {/* Info */}
      <h3 className="font-semibold text-gray-900">{product.name}</h3>
      {product.category && (
        <span className="mt-1 inline-block rounded-full bg-vera-50 px-2 py-0.5 text-xs font-medium text-vera-700">
          {product.category}
        </span>
      )}
      <p className="mt-2 text-lg font-bold text-vera-600">{formattedPrice}</p>
    </Card>
  );
}
