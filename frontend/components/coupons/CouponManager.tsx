"use client";

import { useState, useEffect, useCallback } from "react";
import api from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

interface Coupon {
  id: string;
  code: string;
  discount_percent: number | null;
  discount_fixed_cop: number | null;
  max_uses: number;
  current_uses: number;
  is_active: boolean;
  expires_at: string | null;
  applicable_product_ids: string[];
}

interface Product {
  id: string;
  name: string;
}

export default function CouponManager() {
  const { token, user } = useAuth();
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  
  // Form State
  const [code, setCode] = useState("");
  const [discountType, setDiscountType] = useState<"percent" | "fixed">("percent");
  const [discountValue, setDiscountValue] = useState("");
  const [maxUses, setMaxUses] = useState("10");
  const [expiresAt, setExpiresAt] = useState("");
  const [selectedProductIds, setSelectedProductIds] = useState<string[]>([]);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!token || !user) return;
    setLoading(true);
    
    // Cargar productos de forma independiente para que no bloqueen si falla cupones
    api.get<Product[]>("/products/mine", token)
      .then(data => setProducts(data || []))
      .catch(err => console.error("Error loading products:", err));

    try {
      const couponsData = await api.get<Coupon[]>("/coupons/mine", token);
      setCoupons(couponsData || []);
    } catch (err) {
      console.error("Error fetching coupons:", err);
    } finally {
      setLoading(false);
    }
  }, [token, user]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  async function handleCreateCoupon(e: React.FormEvent) {
    e.preventDefault();
    setCreating(true);
    setError(null);

    const payload = {
      code: code.trim().toUpperCase(),
      discount_percent: discountType === "percent" ? parseFloat(discountValue) : null,
      discount_fixed_cop: discountType === "fixed" ? parseFloat(discountValue) : null,
      max_uses: parseInt(maxUses),
      expires_at: expiresAt ? new Date(expiresAt).toISOString() : null,
      applicable_product_ids: selectedProductIds.length > 0 ? selectedProductIds : null,
    };

    try {
      await api.post("/coupons", payload, token || undefined);
      setShowForm(false);
      resetForm();
      fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear cupón");
    } finally {
      setCreating(false);
    }
  }

  function resetForm() {
    setCode("");
    setDiscountValue("");
    setSelectedProductIds([]);
    setError(null);
  }

  async function handleDelete(id: string) {
    if (!confirm("¿Eliminar este cupón?")) return;
    try {
      await api.delete(`/coupons/${id}`, token || undefined);
      fetchData();
    } catch (err) {
      alert("No se pudo eliminar el cupón");
    }
  }

  const toggleProduct = (id: string) => {
    setSelectedProductIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  if (loading) return (
    <div className="p-8 flex flex-col items-center justify-center text-gray-400 gap-3">
      <div className="w-8 h-8 border-4 border-vera-100 border-t-vera-600 rounded-full animate-spin" />
      <p className="text-sm italic">Cargando tus promociones...</p>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="font-medium text-gray-700">Tus Cupones Activos</h3>
          <button 
            onClick={fetchData}
            className="text-[10px] bg-gray-100 hover:bg-gray-200 text-gray-500 px-2 py-0.5 rounded-full transition-colors"
          >
            🔄 Actualizar
          </button>
        </div>
        <Button size="sm" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancelar" : "+ Nuevo Cupón"}
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleCreateCoupon} className="p-6 rounded-2xl bg-gray-50 border border-gray-100 space-y-4 animate-in fade-in slide-in-from-top-2">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input 
              label="Código (ej: PROMO10)" 
              value={code} 
              onChange={e => setCode(e.target.value)} 
              required 
            />
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium text-gray-700">Tipo de Descuento</label>
              <div className="flex bg-white rounded-xl p-1 border border-gray-200">
                <button
                  type="button"
                  className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${discountType === 'percent' ? 'bg-vera-600 text-white' : 'text-gray-500 hover:bg-gray-50'}`}
                  onClick={() => setDiscountType('percent')}
                >
                  Porcentaje (%)
                </button>
                <button
                  type="button"
                  className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all ${discountType === 'fixed' ? 'bg-vera-600 text-white' : 'text-gray-500 hover:bg-gray-50'}`}
                  onClick={() => setDiscountType('fixed')}
                >
                  Valor Fijo ($)
                </button>
              </div>
            </div>
            <Input 
              label={discountType === 'percent' ? "Porcentaje (1-100)" : "Valor COP"} 
              type="number"
              value={discountValue}
              onChange={e => setDiscountValue(e.target.value)}
              required
            />
            <Input 
              label="Máximo de usos" 
              type="number"
              value={maxUses}
              onChange={e => setMaxUses(e.target.value)}
              required
            />
            <Input 
              label="Fecha expiración (Opcional)" 
              type="datetime-local"
              value={expiresAt}
              onChange={e => setExpiresAt(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Asignar a Productos (Si no seleccionas ninguno, aplica a todo)</label>
              <button 
                type="button" 
                onClick={() => setSelectedProductIds(selectedProductIds.length === products.length ? [] : products.map(p => p.id))}
                className="text-[10px] font-bold text-vera-600 hover:text-vera-700 transition-colors"
              >
                {selectedProductIds.length === products.length ? "Deseleccionar Todo" : "Seleccionar Todo"}
              </button>
            </div>
            <div className="max-h-40 overflow-y-auto p-3 rounded-xl bg-white border border-gray-200 grid gap-2">
              {products.length === 0 ? (
                <div className="py-4 text-center">
                  <p className="text-xs text-gray-400 italic mb-2">No tienes productos activos para asignar.</p>
                  <button type="button" onClick={fetchData} className="text-[10px] text-vera-600 underline">Reintentar carga</button>
                </div>
              ) : (
                products.map(p => (
                  <label key={p.id} className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors group">
                    <input 
                      type="checkbox" 
                      checked={selectedProductIds.includes(p.id)}
                      onChange={() => toggleProduct(p.id)}
                      className="w-4 h-4 text-vera-600 border-gray-300 rounded focus:ring-vera-500 transition-all group-hover:scale-110"
                    />
                    <span className="text-sm text-gray-700 group-hover:text-vera-800 transition-colors">{p.name}</span>
                  </label>
                ))
              )}
            </div>
          </div>

          {error && <p className="text-xs text-red-600">{error}</p>}
          
          <Button type="submit" variant="primary" className="w-full" disabled={creating}>
            {creating ? "Creando..." : "Crear Cupón"}
          </Button>
        </form>
      )}

      <div className="grid gap-3">
        {coupons.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4 italic">No tienes cupones creados aún.</p>
        ) : (
          coupons.map(c => (
            <div key={c.id} className="flex items-center justify-between p-4 rounded-2xl border border-gray-100 bg-white hover:border-vera-100 transition-colors">
              <div>
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded-lg bg-vera-50 text-vera-700 font-mono font-bold text-sm">
                    {c.code}
                  </span>
                  <span className="text-xs font-medium text-gray-500">
                    {c.discount_percent ? `${c.discount_percent}% desc.` : `$${c.discount_fixed_cop?.toLocaleString()} COP desc.`}
                  </span>
                </div>
                <div className="mt-1 flex items-center gap-3 text-[10px] text-gray-400 font-medium">
                  <span>Uso: {c.current_uses}/{c.max_uses}</span>
                  <span>•</span>
                  <span>{c.applicable_product_ids?.length > 0 ? `${c.applicable_product_ids.length} productos` : "Global"}</span>
                  {c.expires_at && (
                    <>
                      <span>•</span>
                      <span>Expira: {new Date(c.expires_at).toLocaleDateString()}</span>
                    </>
                  )}
                </div>
              </div>
              <button 
                onClick={() => handleDelete(c.id)}
                className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                title="Eliminar"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
