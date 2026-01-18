import { useEffect, useState } from "react";
import { healthApi } from "./api/client";
import ArticleList from "./components/ArticleList";
import DiscordPreview from "./components/DiscordPreview";
import FeedForm from "./components/FeedForm";
import FeedList from "./components/FeedList";

/**
 * Main Application Component
 */
function App() {
  const [editingFeed, setEditingFeed] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    checkApiHealth();
  }, []);

  const checkApiHealth = async () => {
    try {
      await healthApi.check();
      setApiStatus("connected");
    } catch (err) {
      setApiStatus("disconnected");
    }
  };

  const handleEdit = (feed) => {
    setEditingFeed(feed);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingFeed(null);
  };

  const handleSave = () => {
    handleCloseForm();
    setRefreshKey((k) => k + 1);
  };

  return (
    <div className="min-h-screen bg-zinc-900">
      {/* Header */}
      <header className="bg-zinc-800 border-b border-zinc-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📰</span>
              <h1 className="text-xl font-bold text-white">Notify Niche</h1>
              <span className="text-sm text-zinc-500">RSS Feed Manager</span>
            </div>

            {/* API Status */}
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full ${
                  apiStatus === "connected"
                    ? "bg-green-500"
                    : apiStatus === "disconnected"
                      ? "bg-red-500"
                      : "bg-yellow-500"
                }`}
              ></span>
              <span className="text-sm text-zinc-400">
                {apiStatus === "connected"
                  ? "API 연결됨"
                  : apiStatus === "disconnected"
                    ? "API 연결 실패"
                    : "확인 중..."}
              </span>
              {apiStatus === "disconnected" && (
                <button
                  onClick={checkApiHealth}
                  className="text-blue-400 hover:text-blue-300 text-sm"
                >
                  재시도
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* API Disconnected Warning */}
      {apiStatus === "disconnected" && (
        <div className="bg-red-900/50 border-b border-red-700 px-6 py-3">
          <div className="max-w-7xl mx-auto flex items-center gap-3 text-red-200 text-sm">
            <span>⚠️</span>
            <span>
              API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.
            </span>
            <code className="bg-red-900 px-2 py-1 rounded text-xs">
              uvicorn api.main:app --reload
            </code>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Feed Management */}
        <section>
          <FeedList onEdit={handleEdit} refresh={refreshKey} />
        </section>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Articles */}
          <section>
            <ArticleList />
          </section>

          {/* Discord Preview */}
          <section>
            <DiscordPreview />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-zinc-800 border-t border-zinc-700 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-center text-sm text-zinc-500">
            Notify Niche • RSS Feed Management & Discord Notification System
          </p>
        </div>
      </footer>

      {/* Feed Form Modal */}
      {showForm && (
        <FeedForm
          feed={editingFeed}
          onClose={handleCloseForm}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

export default App;
