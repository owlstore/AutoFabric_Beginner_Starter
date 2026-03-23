export default function UserBubble({ message }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[85%] flex items-start gap-2.5 flex-row-reverse">
        {/* Avatar */}
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-white text-[11px] font-bold shrink-0">
          U
        </div>
        {/* Bubble */}
        <div className="rounded-2xl rounded-tr-md bg-gradient-to-br from-[#1e293b] to-[#1a1a2e] border border-[#2a2a3e] px-4 py-2.5 text-[13px] text-[#e4e4e7] leading-relaxed whitespace-pre-wrap shadow-lg shadow-black/20">
          {message.content}
        </div>
      </div>
    </div>
  );
}
