import { useEffect, useState } from "react";
import { articlesApi } from "../api/client";

/**
 * Discord Preview Component
 * Shows how messages will appear in Discord
 */
export default function DiscordPreview() {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [limit, setLimit] = useState(5);

  useEffect(() => {
    loadPreview();
  }, [limit]);

  const loadPreview = async () => {
    try {
      setLoading(true);
      const data = await articlesApi.getPreview(null, limit);
      setPreview(data);
    } catch (err) {
      console.error("Failed to load preview:", err);
      setPreview({ header: "⚠️ 미리보기 로드 실패", embeds: [] });
    } finally {
      setLoading(false);
    }
  };

  const getColorStyle = (color) => {
    // Convert decimal to hex
    const hex = color.toString(16).padStart(6, "0");
    return `#${hex}`;
  };

  if (loading) {
    return (
      <div className="bg-zinc-800 rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-zinc-700 rounded w-3/4"></div>
          {[1, 2].map((i) => (
            <div key={i} className="h-24 bg-zinc-700 rounded"></div>
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
          👁️ Discord 미리보기
        </h2>

        <div className="flex items-center gap-3">
          <label className="text-sm text-zinc-400">기사 수:</label>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="bg-zinc-700 text-zinc-200 text-sm rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={3}>3개</option>
            <option value={5}>5개</option>
            <option value={10}>10개</option>
          </select>

          <button
            onClick={loadPreview}
            className="text-zinc-400 hover:text-white transition-colors"
            title="새로고침"
          >
            🔄
          </button>
        </div>
      </div>

      {/* Discord Message Preview */}
      <div className="p-6 bg-discord-darkest">
        {/* Bot Avatar & Header */}
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold shrink-0">
            N
          </div>

          <div className="flex-1 min-w-0">
            {/* Bot Name & Time */}
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-white">Notify Niche</span>
              <span className="text-xs text-zinc-500">오늘 오전 9:00</span>
            </div>

            {/* Message Content */}
            <p className="text-zinc-200 text-sm mb-3">{preview?.header}</p>

            {/* Embeds */}
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {preview?.embeds.map((embed, idx) => (
                <div
                  key={idx}
                  className="discord-embed"
                  style={{ borderLeftColor: getColorStyle(embed.color) }}
                >
                  {embed.url ? (
                    <a
                      href={embed.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="discord-embed-title hover:underline"
                    >
                      {embed.title}
                    </a>
                  ) : (
                    <div className="font-semibold text-white text-sm">
                      {embed.title}
                    </div>
                  )}

                  {embed.description && (
                    <div className="discord-embed-description">
                      {embed.description}
                    </div>
                  )}

                  {embed.footer && (
                    <div className="discord-embed-footer">
                      {embed.footer.text}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {preview?.embeds.length === 0 && (
              <div className="text-center py-8 text-zinc-500">
                미리보기할 기사가 없습니다.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
