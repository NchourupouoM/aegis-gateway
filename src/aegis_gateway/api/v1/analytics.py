from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from aegis_gateway.observability.database import get_db_session
from aegis_gateway.observability.service import FinOpsAnalyticsService

router = APIRouter(prefix="/v1/analytics", tags=["FinOps & Observability"])


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db_session)):
    """Retourne les métriques FinOps et de sécurité au format JSON."""
    return await FinOpsAnalyticsService.get_metrics_summary(db)


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db_session)):
    """Tableau de bord HTML moderne prêt pour la démonstration."""
    metrics = await FinOpsAnalyticsService.get_metrics_summary(db)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Aegis-LLM : FinOps & Observability</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {{
                darkMode: 'class',
                theme: {{
                    extend: {{
                        colors: {{
                            brand: '#3b82f6',
                        }}
                    }}
                }}
            }}
        </script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-8 font-sans">
        <div class="max-w-6xl mx-auto space-y-8">
            <!-- Header -->
            <div class="flex items-center justify-between border-b border-slate-800 pb-6">
                <div>
                    <h1 class="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
                        🛡️ Aegis-LLM Gateway
                        <span class="text-xs uppercase bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full font-semibold border border-emerald-500/30">Live Enterprise</span>
                    </h1>
                    <p class="text-slate-400 text-sm mt-1">Tableau de bord FinOps, Résilience & Sécurité en temps réel</p>
                </div>
                <button onclick="location.reload()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2 rounded-lg text-sm font-medium transition border border-slate-700">
                    🔄 Rafraîchir
                </button>
            </div>

            <!-- FinOps Top Banner (ROI) -->
            <div class="bg-gradient-to-r from-blue-900/40 via-indigo-900/40 to-slate-900/40 border border-blue-500/30 rounded-2xl p-6 shadow-xl flex items-center justify-between">
                <div>
                    <span class="text-xs uppercase tracking-wider font-semibold text-blue-400">Économies FinOps Réalisées (vs 100% GPT-4o)</span>
                    <div class="text-4xl font-black text-white mt-1">${metrics['total_savings_usd']:.4f} <span class="text-emerald-400 text-2xl font-bold">({metrics['savings_percentage']}%)</span></div>
                    <p class="text-xs text-slate-400 mt-1">Coût réel : ${metrics['total_cost_usd']:.4f} | Baseline évitée : ${metrics['baseline_cost_usd']:.4f}</p>
                </div>
                <div class="text-right">
                    <span class="text-xs text-slate-400 uppercase font-semibold">Tokens Traités</span>
                    <div class="text-3xl font-bold text-slate-200">{metrics['total_tokens_processed']:,}</div>
                </div>
            </div>

            <!-- Metrics Grid -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                    <span class="text-xs text-slate-400 uppercase font-semibold">Requêtes Traitées</span>
                    <div class="text-2xl font-bold text-white mt-2">{metrics['total_requests']}</div>
                    <span class="text-xs text-slate-500 mt-1 block">Débit global</span>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                    <span class="text-xs text-slate-400 uppercase font-semibold">Latence Moyenne</span>
                    <div class="text-2xl font-bold text-cyan-400 mt-2">{metrics['avg_latency_ms']} ms</div>
                    <span class="text-xs text-slate-500 mt-1 block">p50 / p95 estimé</span>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                    <span class="text-xs text-slate-400 uppercase font-semibold">Failovers Évités</span>
                    <div class="text-2xl font-bold text-purple-400 mt-2">{metrics['fallbacks_triggered']}</div>
                    <span class="text-xs text-slate-500 mt-1 block">Pannes absorbées transparentes</span>
                </div>

                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
                    <span class="text-xs text-slate-400 uppercase font-semibold">Attaques Bloquées</span>
                    <div class="text-2xl font-bold text-rose-400 mt-2">{metrics['threats_blocked']}</div>
                    <span class="text-xs text-slate-500 mt-1 block">Jailbreaks & Injections stoppés</span>
                </div>
            </div>

            <!-- Security & Compliance Status -->
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
                <h3 class="text-lg font-bold text-white mb-4">Statut Conformité & Confidentialité</h3>
                <div class="flex items-center gap-6">
                    <div class="flex-1 bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <span class="text-xs text-slate-400">Requêtes Anonymisées (PII)</span>
                        <div class="text-xl font-bold text-amber-400 mt-1">{metrics['pii_requests_anonymized']}</div>
                    </div>
                    <div class="flex-1 bg-slate-950 p-4 rounded-lg border border-slate-800">
                        <span class="text-xs text-slate-400">Protection OWASP LLM01 / LLM02</span>
                        <div class="text-xl font-bold text-emerald-400 mt-1">Actif (100%)</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)