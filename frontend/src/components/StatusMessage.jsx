export default function StatusMessage({ type = "info", message }) {
  const styles = {
    info: {
      background: "#f5f5f5",
      color: "#444",
      border: "1px solid #e5e5e5",
    },
    error: {
      background: "#fff1f1",
      color: "#b00020",
      border: "1px solid #f2caca",
    },
    success: {
      background: "#f3fff6",
      color: "#0a7a33",
      border: "1px solid #cfead7",
    },
  };

  const current = styles[type] || styles.info;

  return (
    <div
      style={{
        marginTop: 20,
        padding: 12,
        borderRadius: 12,
        ...current,
      }}
    >
      {message}
    </div>
  );
}
