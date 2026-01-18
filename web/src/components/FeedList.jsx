import { useEffect, useState } from "react";
import { feedsApi } from "../api/client";

/**
 * Feed List Component
 * Displays all RSS feeds with CRUD operations
 */
export default function FeedList({ onEdit, refresh }) {
  const [feeds, setFeeds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    loadFeeds();
  }, [refresh]);

  const loadFeeds = async () => {
    try {
      setLoading(true);
      const data = await feedsApi.getAll();
      setFeeds(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (feed) => {
    try {
      await feedsApi.update(feed.url, { enabled: !feed.enabled });
      loadFeeds();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (feed) => {
    if (!confirm(`"${feed.name || feed.url}" 피드를 삭제하시겠습니까?`)) return;

    try {
      await feedsApi.delete(feed.url);
      loadFeeds();
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredFeeds =
    filter === "all" ? feeds : feeds.filter((f) => f.category === filter);

  const categories = [...new Set(feeds.map((f) => f.category))];

  if (loading) {
    return (
      <div className="bg-zinc-800 rounded-lg p-6">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-zinc-700 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-zinc-700 rounded"></div>
              <div className="h-4 bg-zinc-700 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-800 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-zinc-700 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            📋 피드 관리
            <span className="text-sm font-normal text-zinc-400">
              ({feeds.length}개)
            </span>
          </h2>

          {/* Category Filter */}
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
        </div>

        <button
          onClick={() => onEdit(null)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
        >
          <span>+</span> 새 피드
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-900/50 border border-red-700 rounded text-red-200 text-sm">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-zinc-900/50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">
                카테고리
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">
                이름
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">
                URL
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-zinc-400 uppercase tracking-wider">
                상태
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-zinc-400 uppercase tracking-wider">
                작업
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-700">
            {filteredFeeds.map((feed, idx) => (
              <tr
                key={feed.url}
                className={idx % 2 === 0 ? "bg-zinc-800" : "bg-zinc-800/50"}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-zinc-300">{feed.category}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="font-medium text-white">
                    {feed.name || "-"}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <a
                    href={feed.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-sm truncate block max-w-xs"
                    title={feed.url}
                  >
                    {feed.url.length > 50
                      ? feed.url.substring(0, 50) + "..."
                      : feed.url}
                  </a>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => handleToggle(feed)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      feed.enabled
                        ? "bg-green-900/50 text-green-400 hover:bg-green-900"
                        : "bg-zinc-700 text-zinc-400 hover:bg-zinc-600"
                    }`}
                  >
                    {feed.enabled ? "✅ 활성" : "⏸️ 비활성"}
                  </button>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right">
                  <button
                    onClick={() => onEdit(feed)}
                    className="text-zinc-400 hover:text-blue-400 mr-3 transition-colors"
                    title="수정"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() => handleDelete(feed)}
                    className="text-zinc-400 hover:text-red-400 transition-colors"
                    title="삭제"
                  >
                    🗑️
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredFeeds.length === 0 && (
          <div className="text-center py-12 text-zinc-500">
            등록된 피드가 없습니다.
          </div>
        )}
      </div>
    </div>
  );
}
