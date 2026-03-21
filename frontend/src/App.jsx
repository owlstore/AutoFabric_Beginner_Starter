import WorkbenchPageV2 from "./pages/WorkbenchPageV2";
import { ToastProvider } from "./context/ToastContext";

export default function App() {
  return (
    <ToastProvider>
      <WorkbenchPageV2 />
    </ToastProvider>
  );
}
