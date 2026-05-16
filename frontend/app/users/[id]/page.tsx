"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import ProductCard from "@/components/ProductCard";
import ReportModal from "@/components/ReportModal";
import Button from "@/components/ui/Button";

interface UserPublic {
  id: string;
  name: string;
  role: string;
  reputation: number;
  is_verified: boolean;
  email: string | null;
  phone: string | null;
}

interface UserReputation {
  user_id: string;
  average_rating: number;
  total_reviews: number;
}

interface RatingRead {
  id: string;
  negotiation_id: string;
  reviewer_id: string;
  reviewed_id: string;
  stars: number;
  comment: string | null;
  created_at: string;
}

interface Product {
  id: string;
  name: string;
  price: number;
  image_urls: string[];
  is_active: boolean;
  category: string | null;
  created_at: string;
  updated_at: string;
}

export default function PublicProfilePage() {
  const params = useParams();
  const userId = params?.id as string;
  const router = useRouter();

  const [user, setUser] = useState<UserPublic | null>(null);
  const [reputation, setReputation] = useState<UserReputation | null>(null);
  const [reviews, setReviews] = useState<RatingRead[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isReportOpen, setIsReportOpen] = useState(false);

  useEffect(() => {
    if (!userId) return;

    async function fetchProfileData() {
      setLoading(true);
      try {
        // 1. Fetch user basic info
        const userData = await api.get<UserPublic>(`/users/${userId}`);
        setUser(userData);

        // 2. Fetch reputation (HU 7.2)
        try {
          const repData = await api.get<UserReputation>(`/ratings/user/${userId}/reputation`);
          setReputation(repData);
        } catch (e) {
          // Si falla, asumimos 0
          setReputation({ user_id: userId, average_rating: 0, total_reviews: 0 });
        }

        // 3. Fetch reviews (HU 7.2)
        try {
          const revData = await api.get<RatingRead[]>(`/ratings/user/${userId}`);
          setReviews(revData);
        } catch (e) {
          setReviews([]);
        }

        // 4. Fetch seller products
        if (userData.role === "vendedor") {
          try {
            const prodData = await api.get<Product[]>(`/products/?seller_id=${userId}&limit=20`);
            setProducts(prodData.filter(p => p.is_active));
          } catch (e) {
            setProducts([]);
          }
        }
      } catch (err: any) {
        setError(err.message || "Usuario no encontrado");
      } finally {
        setLoading(false);
      }
    }

    fetchProfileData();
  }, [userId]);

  if (loading) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-8">
        <p className="text-gray-500 animate-pulse">Cargando perfil...</p>
      </main>
    );
  }

  if (error || !user) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-8 text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Perfil no encontrado</h1>
        <p className="text-gray-600 mb-6">{error}</p>
        <Link href="/products" className="text-vera-600 hover:underline">
          ← Volver al catálogo
        </Link>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-10">
      <Link href="/products" className="text-sm text-gray-500 hover:text-vera-600 mb-6 inline-block">
        ← Volver al catálogo
      </Link>

      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-8 flex flex-col md:flex-row md:items-start gap-6">
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              {user.name}
              {user.is_verified && (
                <span className="text-blue-500 text-xl" title="Verificado">✓</span>
              )}
            </h1>
            <button
              onClick={() => setIsReportOpen(true)}
              className="text-gray-400 hover:text-red-500 transition-colors"
              title="Denunciar usuario"
            >
              🚩
            </button>
          </div>
          <p className="text-sm text-gray-500 capitalize mb-4">{user.role}</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm text-gray-700">
            {user.email && <p>📧 {user.email}</p>}
            {user.phone && <p>📱 {user.phone}</p>}
          </div>
        </div>

        <div className="bg-gray-50 p-6 rounded-xl border border-gray-200 min-w-[200px] text-center shrink-0">
          <p className="text-sm font-medium text-gray-500 mb-1">Reputación</p>
          <div className="text-4xl font-bold text-vera-600 mb-1">
            ⭐ {reputation?.average_rating.toFixed(1) || "0.0"}
          </div>
          <p className="text-xs text-gray-500">
            {reputation?.total_reviews || 0} {(reputation?.total_reviews === 1) ? "reseña" : "reseñas"}
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-8">
          {user.role === "vendedor" && (
            <section>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Productos en venta</h2>
              {products.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {products.map(product => (
                    <Link key={product.id} href={`/products/${product.id}`}>
                      <ProductCard product={product} />
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm bg-gray-50 p-4 rounded-xl border border-gray-100">
                  Este vendedor no tiene productos activos en este momento.
                </p>
              )}
            </section>
          )}
        </div>

        <div className="md:col-span-1">
          <section>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Reseñas de Usuarios</h2>
            {reviews.length > 0 ? (
              <div className="space-y-4">
                {reviews.map(review => (
                  <div key={review.id} className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex text-yellow-400 text-sm">
                        {"★".repeat(review.stars)}{"☆".repeat(5 - review.stars)}
                      </div>
                      <span className="text-xs text-gray-400">
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {review.comment ? (
                      <p className="text-sm text-gray-700 italic">"{review.comment}"</p>
                    ) : (
                      <p className="text-sm text-gray-400 italic">Sin comentario</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm bg-gray-50 p-4 rounded-xl border border-gray-100">
                Aún no hay reseñas para este usuario.
              </p>
            )}
          </section>
        </div>
      </div>

      <ReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        reportedUserId={user.id}
        targetName={user.name}
      />
    </main>
  );
}
