import React, { useEffect, useState } from "react";
import { format } from "date-fns";
import { toZonedTime } from "date-fns-tz";

function AdminDashboard() {
    const [data, setData] = useState([]);
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [file, setFile] = useState(null);

    const API_BASE = "https://fuzzy-invention-x6qvq5qqg6pfvrgv-8000.app.github.dev";

    const fetchEvaluations = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams({ fmt: "json" });
            if (startDate) params.append("start", startDate);
            if (endDate) {
                // 終了日を1日進める
                const nextDay = new Date(endDate);
                nextDay.setDate(nextDay.getDate() + 1);
                const nextDayStr = nextDay.toISOString().slice(0, 10);
                params.append("end", nextDayStr);
            }
            const res = await fetch(`${API_BASE}/export/evaluations?${params.toString()}`);
            const json = await res.json();
            setData(json);
        } catch (err) {
            setError("読み込みに失敗しました");
        } finally {
            setLoading(false);
        }
    };

    const downloadCSV = () => {
        const params = new URLSearchParams({ fmt: "csv" });
        if (startDate) params.append("start", startDate);
        if (endDate) {
            // 終了日を1日進めて送信（その日を含めるため）
            const nextDay = new Date(endDate);
            nextDay.setDate(nextDay.getDate() + 1);
            const nextDayStr = nextDay.toISOString().slice(0, 10);
            params.append("end", nextDayStr);
        }
        const url = `${API_BASE}/export/evaluations?${params.toString()}`;
        window.open(url, "_blank");
    };

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);
        try {
            const res = await fetch(`${API_BASE}/upload`, {
                method: "POST",
                body: formData,
            });
            const result = await res.json();
            alert(`アップロード成功: ${result.filename}`);
        } catch (err) {
            alert("アップロードに失敗しました");
        }
    };

    useEffect(() => {
        fetchEvaluations();
        // eslint-disable-next-line
    }, []);

    return (
        <div style={{ padding: 16 }}>
            <h1 style={{ fontSize: 22, fontWeight: "bold", marginBottom: 16 }}>管理ダッシュボード</h1>

            <div style={{ marginBottom: 16, display: "flex", gap: 8 }}>
                <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    style={{ border: "1px solid #ccc", padding: "4px 8px" }}
                />
                <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    style={{ border: "1px solid #ccc", padding: "4px 8px" }}
                />
                <button
                    onClick={fetchEvaluations}
                    style={{
                        background: "#2563eb",
                        color: "#fff",
                        padding: "4px 16px",
                        borderRadius: 4,
                        border: "none",
                        cursor: "pointer",
                    }}
                >
                    再読み込み
                </button>
                <button
                    onClick={downloadCSV}
                    style={{
                        background: "#059669",
                        color: "#fff",
                        padding: "4px 16px",
                        borderRadius: 4,
                        border: "none",
                        cursor: "pointer",
                    }}
                >
                    CSVダウンロード
                </button>
            </div>

            <div style={{ marginBottom: 24 }}>
                <h2 style={{ fontSize: 16, fontWeight: "bold", marginBottom: 4 }}>ファイルアップロード</h2>
                <input type="file" onChange={handleFileChange} style={{ marginBottom: 8 }} />
                <button
                    onClick={handleUpload}
                    style={{
                        background: "#7c3aed",
                        color: "#fff",
                        padding: "4px 16px",
                        borderRadius: 4,
                        border: "none",
                        cursor: "pointer",
                        marginLeft: 8,
                    }}
                >
                    アップロード
                </button>
            </div>

            {loading ? (
                <p>読み込み中...</p>
            ) : error ? (
                <p style={{ color: "#dc2626" }}>{error}</p>
            ) : (
                <table style={{ width: "100%", fontSize: 14, borderCollapse: "collapse", border: "1px solid #ccc" }}>
                    <thead>
                        <tr style={{ background: "#f3f4f6" }}>
                            <th style={{ border: "1px solid #ccc", padding: "4px 8px" }}>日時</th>
                            <th style={{ border: "1px solid #ccc", padding: "4px 8px" }}>質問</th>
                            <th style={{ border: "1px solid #ccc", padding: "4px 8px" }}>回答</th>
                            <th style={{ border: "1px solid #ccc", padding: "4px 8px" }}>スコア</th>
                            <th style={{ border: "1px solid #ccc", padding: "4px 8px" }}>理由</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, idx) => {
                            const jstDate = toZonedTime(new Date(row.created_at), "Asia/Tokyo");
                            return (
                                <tr key={idx} style={{ background: idx % 2 === 0 ? "#fff" : "#f9fafb" }}>
                                    <td style={{ border: "1px solid #ccc", padding: "4px 8px" }}>
                                        {format(jstDate, "yyyy-MM-dd HH:mm")}
                                    </td>
                                    <td style={{ border: "1px solid #ccc", padding: "4px 8px" }}>{row.question}</td>
                                    <td style={{ border: "1px solid #ccc", padding: "4px 8px" }}>{row.answer}</td>
                                    <td style={{ border: "1px solid #ccc", padding: "4px 8px", textAlign: "center" }}>{row.score}</td>
                                    <td style={{ border: "1px solid #ccc", padding: "4px 8px" }}>{row.reason}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            )}

            <div style={{ marginTop: 32 }}>
                <h2 style={{ fontSize: 18, fontWeight: "bold", marginBottom: 8 }}>スコア推移グラフ</h2>
                <img
                    src={`${API_BASE}/metrics/quality/daily.png`}
                    alt="日次スコア推移グラフ"
                    style={{ border: "1px solid #ccc", borderRadius: 4, maxWidth: "100%" }}
                />
            </div>
        </div>
    );
}

export default AdminDashboard;