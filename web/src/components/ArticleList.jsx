import { useEffect, useState } from "react";
import { articlesApi } from "../api/client";

/**
 * Article List Component
 * Displays recent articles from database
 */
export default function ArticleList() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      setLoading(true);
      const data = await articlesApi.getRecent(null, 50);
      setArticles(data);
    } catch (err) {
      console.error("Failed to load articles:", err);
    } finally {
      setLoading(false);
    }
  };

  const priorityIcons = {
    high: "🔥",
    medium: "⭐",
    low: "📌",
  };

  const categories = [
    ...new Set(articles.map((a) => a.category).filter(Boolean)),
  ];
  const filteredArticles =
    filter === "all" ? articles : articles.filter((a) => a.category === filter);

  const formatDate = (dateStr) => {
    if (!dateStr) return "-";
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;

    if (diff < 3600000) return `${Math.floor(diff / 60000)}분 전`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}시간 전`;
    return date.toLocaleDateString("ko-KR", { month: "short", day: "numeric" });
  };

  if (loading) {
    return (
      <div className="bg-zinc-800 rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-zinc-700 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-800 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-zinc-700 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          📜 최근 기사
          <span className="text-sm font-normal text-zinc-400">
            ({articles.length}개)
          </span>
        </h2>

        <div className="flex items-center gap-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-zinc-700 text-zinc-200 text-sm rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">전체 카테고리</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>

          <button
            onClick={loadArticles}
            className="text-zinc-400 hover:text-white transition-colors"
            title="새로고침"
          >
            🔄
          </button>
        </div>
      </div>

      {/* Article List */}
      <div className="divide-y divide-zinc-700 max-h-96 overflow-y-auto">
        {filteredArticles.map((article, idx) => (
          <div
            key={article.link}
            className="px-6 py-3 hover:bg-zinc-700/50 transition-colors"
          >
            <div className="flex items-start gap-3">
              <span className="text-lg mt-0.5">
                {priorityIcons[article.priority] || "•"}
              </span>
              <div className="flex-1 min-w-0">
                <a
                  href={article.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-zinc-200 hover:text-blue-400 font-medium text-sm block truncate transition-colors"
                  title={article.title}
                >
                  {article.title}
                </a>
                <div className="flex items-center gap-2 mt-1 text-xs text-zinc-500">
                  {article.category && (
                    <span className="bg-zinc-700 px-2 py-0.5 rounded">
                      {article.category}
                    </span>
                  )}
                  <span>{formatDate(article.published_at)}</span>
                </div>
              </div>
            </div>
          </div>
        ))}

        {filteredArticles.length === 0 && (
          <div className="text-center py-12 text-zinc-500">
            기사가 없습니다.
          </div>
        )}
      </div>
    </div>
  );
}
