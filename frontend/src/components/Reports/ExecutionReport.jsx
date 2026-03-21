import { useEffect, useState } from "react";
import { loadOutcomeTimeline } from "../../api/client";

function ExecutionTrendChart({ timelineData }) {
  // Logic for rendering a trend chart of execution data
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">Execution Trend</h3>
      <div className="mt-3">
        {/* Visualization of trend here (e.g., using chart.js or other libraries) */}
      </div>
    </div>
  );
}

function FailureReasonAnalysis({ executions }) {
  const failureReasons = executions.filter(exec => exec.status === "failed").map(exec => exec.output_payload?.stderr || "Unknown error");
  const reasonCount = failureReasons.reduce((acc, reason) => {
    acc[reason] = (acc[reason] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">Failure Reasons</h3>
      <div className="mt-3">
        {Object.entries(reasonCount).map(([reason, count]) => (
          <div key={reason} className="py-2">
            <span className="text-sm font-medium text-slate-700">{reason}</span>
            <div className="text-xs text-slate-500">Occurred {count} times</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TaskEfficiencyReport({ executions }) {
  const successfulExecutions = executions.filter(exec => exec.status === "completed" || exec.status === "success");
  const totalExecutions = executions.length;
  const efficiencyRate = (successfulExecutions.length / totalExecutions) * 100;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-base font-semibold text-slate-900">Task Efficiency</h3>
      <div className="mt-3">
        <div className="text-lg font-semibold text-slate-700">Efficiency Rate: {efficiencyRate.toFixed(2)}%</div>
        <div className="text-xs text-slate-500">
          Based on {totalExecutions} executions, {successfulExecutions.length} were successful.
        </div>
      </div>
    </div>
  );
}

export default function ExecutionReport({ outcomeId }) {
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchExecutions() {
      setLoading(true);
      try {
        const data = await loadOutcomeTimeline(outcomeId);
        setExecutions(data.items || []);
      } catch (err) {
        console.error("Error loading executions:", err);
      } finally {
        setLoading(false);
      }
    }

    if (outcomeId) {
      fetchExecutions();
    }
  }, [outcomeId]);

  return (
    <div className="space-y-6">
      {loading ? (
        <div>Loading execution data...</div>
      ) : (
        <>
          <ExecutionTrendChart timelineData={executions} />
          <FailureReasonAnalysis executions={executions} />
          <TaskEfficiencyReport executions={executions} />
        </>
      )}
    </div>
  );
}
