"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import api from "@/lib/api";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";

interface AnalyticsSummary {
  seller_id: string;
  period: string;
  total_transactions: number;
  total_revenue_cop: number;
  total_discount_cop: number;
  net_revenue_cop: number;
  average_order_cop: number;
}

interface AnalyticsTransaction {
  id: string;
  product_name: string;
  total_cop: number;
  completed_at: string;
  quantity: number;
}

const PERIODS = [
  { value: "day", label: "Hoy" },
  { value: "week", label: "Semana" },
  { value: "month", label: "Mes" },
  { value: "semester", label: "Semestre" },
  { value: "all_time", label: "Todo" },
];

export default function DashboardPage() {
  const router = useRouter();
  const { user, token, isAuthenticated, isHydrated, viewMode } = useAuth();
  
  const [period, setPeriod] = useState("month");
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [timeline, setTimeline] = useState<AnalyticsDataPoint[]>([]);
  const [transactions, setTransactions] = useState<AnalyticsTransaction[]>([]);
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isHydrated && !isAuthenticated) {
      router.push("/auth");
    }
    if (isHydrated && viewMode !== "vendedor") {
      router.push("/profile");
    }
  }, [isHydrated, isAuthenticated, viewMode, router]);

  useEffect(() => {
    if (!token || !isAuthenticated || viewMode !== "vendedor") return;

    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [sumData, timeData, transData] = await Promise.all([
          api.get<AnalyticsSummary>(`/analytics/summary?period=${period}`, token),
          api.get<AnalyticsDataPoint[]>(`/analytics/timeline?period=${period}`, token),
          api.get<AnalyticsTransaction[]>(`/analytics/transactions?period=${period}`, token),
        ]);
        setSummary(sumData);
        setTimeline(timeData);
        setTransactions(transData);
      } catch (err) {
        setError("Error al cargar datos financieros.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [period, token, isAuthenticated, viewMode]);

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "COP",
      maximumFractionDigits: 0,
    }).format(val);
  };

  const sortedTransactions = [...transactions].sort((a, b) => {
    const factor = sortOrder === "desc" ? -1 : 1;
    return (new Date(a.completed_at).getTime() - new Date(b.completed_at).getTime()) * factor;
  });

  if (!isHydrated || loading && !summary) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-vera-200 border-t-vera-600 rounded-full animate-spin" />
          <p className="text-gray-500 font-medium">Analizando finanzas...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 pb-20 pt-10">
      <div className="max-w-5xl mx-auto px-4">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10">
          <div>
            <h1 className="text-3xl font-black text-gray-900 tracking-tight">Mi Dashboard Financiero</h1>
            <p className="text-gray-500">Resumen de ventas y métricas de tu emprendimiento.</p>
          </div>
          
          <div className="flex bg-white p-1 rounded-2xl shadow-sm border border-gray-200 overflow-x-auto no-scrollbar">
            {PERIODS.map((p) => (
              <button
                key={p.value}
                onClick={() => setPeriod(p.value)}
                className={`px-4 py-2 text-xs font-bold rounded-xl transition-all whitespace-nowrap ${
                  period === p.value 
                    ? "bg-vera-600 text-white shadow-md shadow-vera-600/30" 
                    : "text-gray-500 hover:bg-gray-50"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-50 text-red-700 rounded-2xl border border-red-100 flex items-center gap-3">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {[
            { label: "Ventas Netas", value: formatCurrency(summary?.net_revenue_cop || 0), icon: "💰", color: "bg-emerald-500" },
            { label: "Pedidos", value: summary?.total_transactions || 0, icon: "📦", color: "bg-blue-500" },
            { label: "Ticket Promedio", value: formatCurrency(summary?.average_order_cop || 0), icon: "📈", color: "bg-purple-500" },
            { label: "Descuentos", value: formatCurrency(summary?.total_discount_cop || 0), icon: "🏷️", color: "bg-orange-500" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card className="p-6 bg-white/80 backdrop-blur-md border-white/40 shadow-xl shadow-black/5 rounded-3xl relative overflow-hidden group">
                <div className={`absolute top-0 right-0 w-16 h-16 ${stat.color} opacity-10 rounded-bl-full transition-transform group-hover:scale-125`} />
                <span className="text-2xl mb-2 block">{stat.icon}</span>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">{stat.label}</p>
                <p className="text-2xl font-black text-gray-900 mt-1">{stat.value}</p>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Timeline Chart */}
        <Card className="p-8 bg-white/40 backdrop-blur-xl border-white/60 shadow-2xl shadow-black/5 rounded-[2.5rem] mb-10 overflow-hidden relative">
          <div className="absolute top-0 right-0 w-64 h-64 bg-vera-100/30 blur-3xl -z-10 rounded-full -mr-32 -mt-32" />
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-10 gap-4">
            <div>
              <h2 className="text-2xl font-black text-gray-900">Tendencia de Ingresos</h2>
              <p className="text-sm text-gray-400 font-medium">Visualización por periodo: {PERIODS.find(p => p.value === period)?.label}</p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 rounded-2xl border border-emerald-100">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider">En Vivo</span>
            </div>
          </div>
          <div className="h-72 w-full flex items-end gap-1 px-2 relative">
            {timeline.length === 0 ? (
              <div className="w-full h-full flex flex-col items-center justify-center text-gray-400 gap-3">
                <div className="w-12 h-12 bg-gray-100 rounded-2xl flex items-center justify-center text-xl">📊</div>
                <p className="italic text-sm font-medium">Sin datos para este periodo.</p>
              </div>
            ) : (
              timeline.map((point, i) => {
                const maxRevenue = Math.max(...timeline.map(p => p.revenue_cop), 1);
                const height = (point.revenue_cop / maxRevenue) * 100;
                return (
                  <div key={point.date} className="group relative flex-1 flex flex-col items-center h-full justify-end">
                    <motion.div
                      initial={{ height: 0 }}
                      animate={{ height: `${Math.max(height, 2)}%` }}
                      transition={{ delay: i * 0.02 }}
                      className={`w-full rounded-t-xl transition-all duration-300 relative group-hover:z-20 ${
                        height > 0 ? "bg-gradient-to-t from-vera-600 to-vera-400" : "bg-gray-100"
                      }`}
                    />
                    <div className="absolute -top-12 opacity-0 group-hover:opacity-100 transition-all bg-gray-900 text-white p-2 rounded-lg text-[10px] z-30 pointer-events-none">
                      {formatCurrency(point.revenue_cop)}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </Card>

        {/* Detailed Transactions List */}
        <Card className="p-8 bg-white shadow-xl shadow-black/5 rounded-[2.5rem]">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-black text-gray-900">Ventas Detalladas</h2>
              <p className="text-sm text-gray-400">Listado individual de pedidos completados</p>
            </div>
            <button 
              onClick={() => setSortOrder(sortOrder === "desc" ? "asc" : "desc")}
              className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl text-xs font-bold transition-colors"
            >
              Ordenar: {sortOrder === "desc" ? "Más Recientes" : "Más Antiguos"}
            </button>
          </div>

          <div className="space-y-3">
            {sortedTransactions.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <p className="text-3xl mb-2">🛍️</p>
                <p className="font-medium italic">Aún no hay ventas registradas en este periodo.</p>
              </div>
            ) : (
              sortedTransactions.map((tx) => (
                <motion.div 
                  key={tx.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-5 bg-gray-50/50 rounded-3xl border border-gray-100 hover:border-vera-200 hover:bg-white hover:shadow-lg hover:shadow-black/5 transition-all"
                >
                  <div className="flex items-center gap-5">
                    <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center text-xl shadow-sm">
                      ✨
                    </div>
                    <div>
                      <p className="font-bold text-gray-900">{tx.product_name || "Producto VeraMarket"}</p>
                      <p className="text-xs text-gray-400">
                        {new Date(tx.completed_at).toLocaleDateString("es-CO", { 
                          day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" 
                        })}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-black text-emerald-600">{formatCurrency(tx.total_cop)}</p>
                    <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Cant: {tx.quantity}</p>
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </Card>

        <div className="mt-10 text-center">
           <Button variant="outline" onClick={() => router.push("/profile")}>
              Volver a mi Perfil
           </Button>
        </div>
      </div>
    </main>
  );
}
