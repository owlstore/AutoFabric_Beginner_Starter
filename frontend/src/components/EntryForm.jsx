export default function EntryForm({
  userInput,
  setUserInput,
  sourceType,
  setSourceType,
  sourceRef,
  setSourceRef,
  notes,
  setNotes,
  handleSubmit,
  isSubmitting
}) {
  return (
    <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
      <h2>极简入口</h2>

      <div style={{ marginTop: 12 }}>
        <div>你想完成什么？</div>
        <textarea
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          style={{ width: "100%", minHeight: 120, marginTop: 8, padding: 12, borderRadius: 12, border: "1px solid #ddd" }}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 12 }}>
        <div>
          <div>资料类型（可选）</div>
          <input
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
            style={{ width: "100%", marginTop: 8, padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
          />
        </div>
        <div>
          <div>资料地址（可选）</div>
          <input
            value={sourceRef}
            onChange={(e) => setSourceRef(e.target.value)}
            style={{ width: "100%", marginTop: 8, padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
          />
        </div>
      </div>

      <div style={{ marginTop: 12 }}>
        <div>补充说明（可选）</div>
        <input
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          style={{ width: "100%", marginTop: 8, padding: 10, borderRadius: 12, border: "1px solid #ddd" }}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={isSubmitting || !userInput.trim()}
        style={{
          marginTop: 16,
          padding: "12px 18px",
          borderRadius: 12,
          border: 0,
          background: "#111",
          color: "#fff",
          cursor: "pointer",
          fontSize: 16,
          fontWeight: 600
        }}
      >
        {isSubmitting ? "提交中..." : "开始推进"}
      </button>
    </div>
  );
}
