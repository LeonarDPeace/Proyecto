"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

interface GmvSummary {
  total_transactions: number;
  total_gmv_cop: number;
  period: string;
}

interface PendingReport {
  id: string;
  reason: string;
  description: string;
  product_id: string;
  reported_user_id: string;
  status: string;
  created_at: string;
}

export default function AdminPage() {
  const router = useRouter();
  const { user, token, isAuthenticated, isHydrated } = useAuth();
  
  const [gmv, setGmv] = useState<GmvSummary | null>(null);
  const [reports, setReports] = useState<PendingReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isHydrated && (!isAuthenticated || user?.role !== "admin")) {
      router.push("/");
    }
  }, [isHydrated, isAuthenticated, user, router]);

  useEffect(() => {
    if (!token || user?.role !== "admin") return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const [gmvData, reportsData] = await Promise.all([
          api.get<GmvSummary>("/negotiations/metrics/gmv", token),
          api.get<PendingReport[]>("/reports/admin/pending", token),
        ]);
        setGmv(gmvData);
        setReports(reportsData);
      } catch (err) {
        console.error("Error fetching admin data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token, user]);

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(val);
  };

  const handleReview = async (reportId: string, status: "resolved" | "dismissed") => {
    if (!token) return;
    try {
      await api.patch(`/reports/admin/${reportId}?new_status=${status}`, {}, token);
      setReports((prev) => prev.filter((r) => r.id !== reportId));
    } catch (err) {
      alert("Error al procesar reporte");
    }
  };

  if (!isHydrated || user?.role !== "admin") return null;

  return (
    <main className="min-h-screen bg-gray-50 pb-20 pt-10">
      <div className="max-w-5xl mx-auto px-4">
        <h1 className="text-3xl font-black text-gray-900 mb-2">Panel de Administración</h1>
        <p className="text-gray-500 mb-10">Control global y moderación del campus.</p>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Métricas Globales */}
          <section>
            <h2 className="text-xl font-bold text-gray-800 mb-4">Salud del Mercado</h2>
            <Card className="p-8 bg-vera-600 text-white shadow-xl shadow-vera-600/20 rounded-3xl">
              <p className="text-vera-100 text-xs font-bold uppercase tracking-widest mb-1">Volumen Total (GMV)</p>
              <p className="text-4xl font-black mb-6">
                {loading ? "..." : formatCurrency(gmv?.total_gmv_cop || 0)}
              </p>
              <div className="flex justify-between items-end border-t border-white/20 pt-4">
                <div>
                  <p className="text-vera-100 text-[10px] uppercase font-bold">Transacciones</p>
                  <p className="text-xl font-bold">{gmv?.total_transactions || 0}</p>
                </div>
                <div className="text-right">
                  <p className="text-vera-100 text-[10px] uppercase font-bold">Estado</p>
                  <p className="text-sm font-bold text-emerald-300">● Sistema Activo</p>
                </div>
              </div>
            </Card>
          </section>

          {/* Moderación */}
          <section>
            <h2 className="text-xl font-bold text-gray-800 mb-4">Reportes Pendientes</h2>
            <div className="space-y-4">
              {loading ? (
                <p className="text-gray-400">Cargando reportes...</p>
              ) : reports.length === 0 ? (
                <Card className="p-10 text-center text-gray-400 border-dashed bg-white">
                  No hay reportes pendientes de revisión. ✨
                </Card>
              ) : (
                reports.map((report) => (
                  <Card key={report.id} className="p-5 bg-white shadow-sm border border-gray-100 rounded-2xl">
                    <div className="flex justify-between items-start mb-2">
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 text-[10px] font-black uppercase rounded">
                        {report.reason}
                      </span>
                      <span className="text-[10px] text-gray-400 font-medium">
                        {new Date(report.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 font-medium mb-4">{report.description}</p>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" className="text-xs border-red-200 text-red-600 hover:bg-red-50" onClick={() => handleReview(report.id, "resolved")}>
                        Bloquear
                      </Button>
                      <Button size="sm" variant="outline" className="text-xs" onClick={() => handleReview(report.id, "dismissed")}>
                        Desestimar
                      </Button>
                    </div>
                  </Card>
                ))
              )}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
