"use client";

/**
 * ProductForm — Formulario reutilizable para crear y editar productos (Sprint 3).
 *
 * En modo "create" envía POST /products/.
 * En modo "edit" envía PUT /products/{id}.
 * Soporta carga de imágenes desde dispositivo (convertidas a base64 data URI)
 * y URLs de imagen.
 */

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";

import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

interface ProductFormData {
  name: string;
  description: string;
  price: string;
  category: string;
  stock: string;
  discount_percentage: string;
  warranty_days: string;
  is_returnable: boolean;
  fulfillment_type: string;
}

interface ProductFormProps {
  mode: "create" | "edit";
  productId?: string;
  initialData?: ProductFormData & { image_urls?: string, payment_methods?: string[] };
}

const CATEGORIES = [
  { value: "comida", label: "🍔 Comida/Supermercado" },
  { value: "tecnologia", label: "💻 Tecnología" },
  { value: "moda", label: "👕 Moda" },
  { value: "hogar", label: "🛋️ Hogar" },
  { value: "deportes", label: "⚽ Deportes" },
  { value: "belleza", label: "💅 Belleza" },
  { value: "academico", label: "📚 Académico" },
  { value: "entretenimiento", label: "🎮 Entretenimiento" },
  { value: "servicios", label: "🔧 Servicios" },
  { value: "vehiculos", label: "🚗 Vehículos" },
  { value: "otros", label: "📦 Otros" },
];

const MAX_IMAGES = 5;
const MAX_FILE_SIZE_MB = 2;

export default function ProductForm({
  mode,
  productId,
  initialData,
}: ProductFormProps) {
  const router = useRouter();
  const { token } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [form, setForm] = useState<ProductFormData>({
    name: initialData?.name || "",
    description: initialData?.description || "",
    price: initialData?.price || "",
    category: initialData?.category || "comida",
    stock: initialData?.stock || "1",
    discount_percentage: initialData?.discount_percentage || "0",
    warranty_days: initialData?.warranty_days || "0",
    is_returnable: initialData?.is_returnable || false,
    fulfillment_type: initialData?.fulfillment_type || "merchant",
  });
  
  const [paymentMethods, setPaymentMethods] = useState<string[]>(initialData?.payment_methods || ["efectivo"]);

  // Image management: list of URLs (can be external URLs or base64 data URIs)
  const [imageUrls, setImageUrls] = useState<string[]>(() => {
    if (initialData?.image_urls) {
      return initialData.image_urls
        .split(",")
        .map((u) => u.trim())
        .filter(Boolean);
    }
    return [];
  });
  const [urlInput, setUrlInput] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function handleChange(
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) {
    const value = e.target.type === "checkbox" ? (e.target as HTMLInputElement).checked : e.target.value;
    setForm((prev) => ({ ...prev, [e.target.name]: value }));
  }

  function handlePaymentMethodToggle(method: string) {
    setPaymentMethods(prev => 
      prev.includes(method) ? prev.filter(m => m !== method) : [...prev, method]
    );
  }

  // --- Image handling ---

  function addUrlImage() {
    const url = urlInput.trim();
    if (!url) return;
    if (imageUrls.length >= MAX_IMAGES) {
      setError(`Máximo ${MAX_IMAGES} imágenes.`);
      return;
    }
    setImageUrls((prev) => [...prev, url]);
    setUrlInput("");
    setError(null);
  }

  function removeImage(index: number) {
    setImageUrls((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files) return;

    const remaining = MAX_IMAGES - imageUrls.length;
    if (remaining <= 0) {
      setError(`Máximo ${MAX_IMAGES} imágenes.`);
      return;
    }

    const filesToProcess = Array.from(files).slice(0, remaining);
    setError(null);

    for (const file of filesToProcess) {
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        setError(
          `"${file.name}" excede ${MAX_FILE_SIZE_MB}MB. Usa una imagen más liviana.`,
        );
        continue;
      }

      const dataUri = await fileToBase64(file);
      setImageUrls((prev) => [...prev, dataUri]);
    }

    // Reset file input so the same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  // --- Submit ---

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const price = parseFloat(form.price);
    if (isNaN(price) || price <= 0) {
      setError("El precio debe ser mayor a 0.");
      setSubmitting(false);
      return;
    }

    if (imageUrls.length > MAX_IMAGES) {
      setError(`Máximo ${MAX_IMAGES} imágenes.`);
      setSubmitting(false);
      return;
    }

    const payload = {
      name: form.name,
      description: form.description || null,
      price,
      category: form.category || null,
      image_urls: imageUrls,
      stock: parseInt(form.stock) || 0,
      discount_percentage: parseFloat(form.discount_percentage) || 0.0,
      warranty_days: parseInt(form.warranty_days) || 0,
      is_returnable: form.is_returnable,
      fulfillment_type: form.fulfillment_type,
      payment_methods: paymentMethods,
    };

    try {
      if (mode === "create") {
        await api.post("/products/", payload, token || undefined);
      } else {
        await api.put(`/products/${productId}`, payload, token || undefined);
      }
      router.push("/products");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Error al guardar el producto.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  const formattedPreview =
    form.price && !isNaN(parseFloat(form.price))
      ? new Intl.NumberFormat("es-CO", {
          style: "currency",
          currency: "COP",
          minimumFractionDigits: 0,
        }).format(parseFloat(form.price))
      : "—";

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Input
        label="Nombre del producto"
        name="name"
        value={form.name}
        onChange={handleChange}
        placeholder="Ej: Audífonos Bluetooth"
        required
      />

      <div className="w-full">
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Descripción
        </label>
        <textarea
          name="description"
          value={form.description}
          onChange={handleChange}
          rows={3}
          placeholder="Describe tu producto..."
          className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:border-vera-500 focus:outline-none focus:ring-1 focus:ring-vera-500"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <Input
            label="Precio (COP)"
            name="price"
            type="number"
            min="0"
            step="any"
            value={form.price}
            onChange={handleChange}
            placeholder="5000"
            required
          />
          <p className="mt-1 text-xs text-gray-400">
            Vista previa:{" "}
            <span className="font-semibold text-vera-600">
              {formattedPreview}
            </span>
          </p>
        </div>

        <div className="w-full">
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Categoría
          </label>
          <select
            name="category"
            value={form.category}
            onChange={handleChange}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-vera-500 focus:outline-none focus:ring-1 focus:ring-vera-500"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Input
          label="Stock disponible"
          name="stock"
          type="number"
          min="0"
          value={form.stock}
          onChange={handleChange}
          required
        />
        <Input
          label="Descuento (%)"
          name="discount_percentage"
          type="number"
          min="0"
          max="100"
          step="0.1"
          value={form.discount_percentage}
          onChange={handleChange}
        />
        <Input
          label="Garantía (días)"
          name="warranty_days"
          type="number"
          min="0"
          value={form.warranty_days}
          onChange={handleChange}
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 bg-gray-50 p-4 rounded-lg border border-gray-200">
        <div>
          <label className="flex items-center gap-2 cursor-pointer mb-2">
            <input 
              type="checkbox"
              name="is_returnable"
              checked={form.is_returnable}
              onChange={handleChange}
              className="text-vera-600 focus:ring-vera-500 rounded"
            />
            <span className="text-sm font-medium text-gray-700">Acepta devoluciones</span>
          </label>
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Tipo de Entrega</label>
            <select
              name="fulfillment_type"
              value={form.fulfillment_type}
              onChange={handleChange}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-vera-500 focus:outline-none focus:ring-1 focus:ring-vera-500"
            >
              <option value="merchant">Acordar con vendedor</option>
              <option value="veramarket">VeraMarket Delivery</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Medios de Pago</label>
          <div className="space-y-2">
            {["efectivo", "transferencia", "tarjeta"].map(method => (
              <label key={method} className="flex items-center gap-2 cursor-pointer">
                <input 
                  type="checkbox"
                  checked={paymentMethods.includes(method)}
                  onChange={() => handlePaymentMethodToggle(method)}
                  className="text-vera-600 focus:ring-vera-500 rounded"
                />
                <span className="text-sm text-gray-600 capitalize">{method}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* ── Imágenes ── */}
      <div className="w-full">
        <label className="mb-2 block text-sm font-medium text-gray-700">
          Imágenes ({imageUrls.length}/{MAX_IMAGES})
        </label>

        {/* Preview grid */}
        {imageUrls.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-3">
            {imageUrls.map((url, i) => (
              <div
                key={i}
                className="group relative h-20 w-20 overflow-hidden rounded-lg border border-gray-200 bg-gray-50"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={url}
                  alt={`Foto ${i + 1}`}
                  className="h-full w-full object-cover"
                />
                <button
                  type="button"
                  onClick={() => removeImage(i)}
                  className="absolute inset-0 flex items-center justify-center bg-black/50 text-white opacity-0 transition-opacity group-hover:opacity-100"
                  title="Quitar imagen"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Upload from device */}
        {imageUrls.length < MAX_IMAGES && (
          <div className="mb-3">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileUpload}
              className="hidden"
              id="image-upload"
            />
            <label
              htmlFor="image-upload"
              className="inline-flex cursor-pointer items-center gap-2 rounded-lg border-2 border-dashed border-vera-300 bg-vera-50/50 px-4 py-3 text-sm font-medium text-vera-700 transition-colors hover:bg-vera-100 hover:border-vera-400"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="h-5 w-5"
              >
                <path
                  fillRule="evenodd"
                  d="M1 8a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 018.07 3h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0016.07 6H17a2 2 0 012 2v7a2 2 0 01-2 2H3a2 2 0 01-2-2V8zm13.5 3a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM10 14a3 3 0 100-6 3 3 0 000 6z"
                  clipRule="evenodd"
                />
              </svg>
              Subir desde dispositivo
            </label>
            <p className="mt-1 text-xs text-gray-400">
              Máx. {MAX_FILE_SIZE_MB}MB por archivo. JPG, PNG, WebP.
            </p>
          </div>
        )}

        {/* Or add by URL */}
        {imageUrls.length < MAX_IMAGES && (
          <div className="flex gap-2">
            <input
              type="url"
              value={urlInput}
              onChange={(e) => setUrlInput(e.target.value)}
              placeholder="https://ejemplo.com/foto.jpg"
              className="block flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm placeholder:text-gray-400 focus:border-vera-500 focus:outline-none focus:ring-1 focus:ring-vera-500"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addUrlImage();
                }
              }}
            />
            <Button
              type="button"
              variant="outline"
              size="md"
              onClick={addUrlImage}
            >
              + URL
            </Button>
          </div>
        )}
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <div className="flex gap-3">
        <Button type="submit" disabled={submitting} variant="primary" size="lg">
          {submitting
            ? "Guardando…"
            : mode === "create"
              ? "Publicar Producto"
              : "Guardar Cambios"}
        </Button>
        <Button
          type="button"
          variant="outline"
          size="lg"
          onClick={() => router.back()}
        >
          Cancelar
        </Button>
      </div>
    </form>
  );
}
