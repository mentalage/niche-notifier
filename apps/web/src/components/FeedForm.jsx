import { useEffect, useState } from "react";
import { categoriesApi, feedsApi } from "../api/client";

/**
 * Feed Form Component
 * Modal form for creating/editing feeds
 */
export default function FeedForm({ feed, onClose, onSave }) {
  const [formData, setFormData] = useState({
    url: "",
    name: "",
    category: "",
    enabled: true,
  });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCategories();
    if (feed) {
      setFormData({
        url: feed.url || "",
        name: feed.name || "",
        category: feed.category || "",
        enabled: feed.enabled ?? true,
      });
    }
  }, [feed]);

  const loadCategories = async () => {
    try {
      const data = await categoriesApi.getAll();
      setCategories(data);
      if (!feed && data.length > 0) {
        setFormData((prev) => ({ ...prev, category: data[0].name }));
      }
    } catch (err) {
      console.error("Failed to load categories:", err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (feed) {
        // Update existing feed
        await feedsApi.update(feed.url, {
          name: formData.name || null,
          category: formData.category,
          enabled: formData.enabled,
        });
      } else {
        // Create new feed
        await feedsApi.create(formData);
      }
      onSave();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-zinc-800 rounded-lg w-full max-w-md mx-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-zinc-700 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">
            {feed ? "피드 수정" : "새 피드 추가"}
          </h3>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-900/50 border border-red-700 rounded text-red-200 text-sm">
              {error}
            </div>
          )}

          {/* URL */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              RSS URL <span className="text-red-400">*</span>
            </label>
            <input
              type="url"
              required
              disabled={!!feed}
              value={formData.url}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, url: e.target.value }))
              }
              placeholder="https://example.com/rss"
              className={`w-full bg-zinc-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                feed ? "opacity-50 cursor-not-allowed" : ""
              }`}
            />
            {feed && (
              <p className="mt-1 text-xs text-zinc-500">
                URL은 수정할 수 없습니다.
              </p>
            )}
          </div>

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              표시 이름
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, name: e.target.value }))
              }
              placeholder="예: GeekNews"
              className="w-full bg-zinc-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-zinc-300 mb-2">
              카테고리 <span className="text-red-400">*</span>
            </label>
            <select
              required
              value={formData.category}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, category: e.target.value }))
              }
              className="w-full bg-zinc-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map((cat) => (
                <option key={cat.name} value={cat.name}>
                  {cat.emoji} {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Enabled */}
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="enabled"
              checked={formData.enabled}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, enabled: e.target.checked }))
              }
              className="w-4 h-4 rounded bg-zinc-700 border-zinc-600 text-blue-500 focus:ring-blue-500"
            />
            <label htmlFor="enabled" className="text-sm text-zinc-300">
              피드 활성화
            </label>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded-lg transition-colors"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              {loading ? "저장 중..." : feed ? "수정" : "추가"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
